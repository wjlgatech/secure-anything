"""Ed25519 signing seam for the audit ledger (ADR-003).

Hash-chaining proves a ledger's *internal consistency* — but an operator who can
rewrite rows can recompute every downstream hash and present a self-consistent
forgery. Signing the chain head with a private key the operator does not control
turns "consistent" into "authentic": forging history now requires the key, not just
DB write access. This is what makes Phase-2 "operator-tamper detectable" real.

The `Signer` protocol is the seam. `Ed25519Signer` is the real body; tests can inject
any signer. `cryptography` is imported lazily so this module (and the app) still load
where the extra isn't installed — signing is optional at runtime (ledger accepts
signer=None and behaves exactly as the unsigned chain did).
"""
from __future__ import annotations

import base64
from pathlib import Path
from typing import Protocol, runtime_checkable


@runtime_checkable
class Signer(Protocol):
    def sign(self, message: bytes) -> str: ...            # base64 signature
    def verify(self, message: bytes, signature: str) -> bool: ...
    def public_key_hex(self) -> str: ...


class Ed25519Signer:
    """Deterministic Ed25519 signatures over arbitrary bytes. Compact (64-byte sigs,
    32-byte keys), native, and deterministic by spec — matching the AEGIS prior art."""

    def __init__(self, private_key=None) -> None:
        from cryptography.hazmat.primitives.asymmetric import ed25519

        self._key = private_key or ed25519.Ed25519PrivateKey.generate()
        self._pub = self._key.public_key()

    def sign(self, message: bytes) -> str:
        return base64.b64encode(self._key.sign(message)).decode()

    def verify(self, message: bytes, signature: str) -> bool:
        from cryptography.exceptions import InvalidSignature

        try:
            self._pub.verify(base64.b64decode(signature), message)
            return True
        except (InvalidSignature, ValueError):
            return False

    def public_key_hex(self) -> str:
        from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

        return self._pub.public_bytes(Encoding.Raw, PublicFormat.Raw).hex()

    # --- key persistence (PKCS8 PEM, 0600) ---------------------------------------
    def save_private_key(self, path: Path, password: str | None = None) -> None:
        from cryptography.hazmat.primitives.serialization import (
            BestAvailableEncryption,
            Encoding,
            NoEncryption,
            PrivateFormat,
        )

        enc = BestAvailableEncryption(password.encode()) if password else NoEncryption()
        pem = self._key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, enc)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(pem)
        path.chmod(0o600)

    @classmethod
    def load(cls, path: Path, password: str | None = None) -> Ed25519Signer:
        from cryptography.hazmat.primitives.serialization import load_pem_private_key

        key = load_pem_private_key(
            path.read_bytes(), password.encode() if password else None
        )
        return cls(private_key=key)
