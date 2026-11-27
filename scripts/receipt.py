#!/usr/bin/env python3
"""Run receipts: the only on-disk evidence that moves the north star.

A receipt is what a capability's gate left behind when it actually ran: the exit code the
OS returned (never typed in), hashes of what it printed and wrote, the target it ran on, and
the controls it bears on. Each receipt is appended to a hash-chained ledger
(`runs/ledger.jsonl`, the core's `compute_hash`) and every chain head is Ed25519-signed (the
core's `Ed25519Signer`, ADR-003). The private key never enters the repo; the public key does
(`runs/receipts.pub`), so anyone can re-verify offline.

    receipt.py run    --capability ID --target REPO@SHA --tool-version V [--report FILE] \
                      [--summary TEXT] [--counts JSON] [--triage TEXT] [--phase before|after] \
                      [--cwd DIR] -- <command...>
    receipt.py record --capability ID ... --exit-code N --ran-on URL --evidence-url URL
                      (a run that happened elsewhere, e.g. a CI job; marked observed=remote)
    receipt.py verify  every receipt file is in the ledger once, the chain recomputes, every
                      signature verifies against runs/receipts.pub. Offline; exit 1 on any gap.

Raw tool reports stay OUTSIDE the repo (they quote private source); the receipt pins them by
sha256. The maker is not the checker: `verify` re-derives everything from the files on disk.
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from secure_anything.gate import GateResult  # noqa: E402
from secure_anything.ledger import GENESIS, compute_hash  # noqa: E402
from secure_anything.spec import load_spec  # noqa: E402

RUNS = ROOT / "runs"
KIND = "gate_run"
DEFAULT_KEY = Path(
    os.environ.get("SECURE_ANYTHING_RECEIPT_KEY",
                   Path.home() / ".secure-anything" / "receipts-ed25519.pem")
)


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: Path) -> str:
    return sha256_bytes(p.read_bytes())


def _ledger(runs: Path) -> Path:
    return runs / "ledger.jsonl"


def _entries(runs: Path) -> list[dict]:
    f = _ledger(runs)
    if not f.exists():
        return []
    return [json.loads(line) for line in f.read_text().splitlines() if line.strip()]


def load_signer(key: Path, runs: Path):
    """Load (or create once) the receipt key; refuse a key that does not match the
    committed public key — a second key would silently fork the evidence trail."""
    from secure_anything.signing import Ed25519Signer

    if key.exists():
        signer = Ed25519Signer.load(key)
    else:
        signer = Ed25519Signer()
        signer.save_private_key(key)
    pub = runs / "receipts.pub"
    if pub.exists():
        if pub.read_text().strip() != signer.public_key_hex():
            raise SystemExit(f"receipt key {key} does not match {pub} — refusing to fork the chain")
    else:
        runs.mkdir(parents=True, exist_ok=True)
        pub.write_text(signer.public_key_hex() + "\n")
    return signer


def append(receipt: dict, *, runs: Path, signer) -> Path:
    entries = _entries(runs)
    prev = entries[-1]["hash"] if entries else GENESIS
    h = compute_hash(prev, KIND, receipt)
    entry = {"seq": len(entries) + 1, "kind": KIND, "receipt": receipt["id"],
             "capability": receipt["capability"], "prev_hash": prev, "hash": h,
             "signature": signer.sign(h.encode())}
    out = runs / receipt["capability"] / f"{receipt['id']}.json"
    if out.exists():
        raise SystemExit(f"{out} exists — receipts are append-only")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    with _ledger(runs).open("a") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")
    return out


def _verify_sig(pub_hex: str, message: bytes, signature: str) -> bool:
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

    try:
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(pub_hex)).verify(
            base64.b64decode(signature), message)
        return True
    except (InvalidSignature, ValueError):
        return False


def verify(runs: Path = RUNS) -> list[str]:
    """Every problem found; an empty list means every receipt is chained and signed."""
    bad: list[str] = []
    files = {p.stem: p for p in runs.glob("*/*.json")}
    entries = _entries(runs)
    if not files and not entries:
        return bad
    pub = runs / "receipts.pub"
    if not pub.exists():
        return [f"{pub.relative_to(runs.parent)} is missing — receipts cannot be verified"]
    pub_hex = pub.read_text().strip()
    prev, seen = GENESIS, set()
    for e in entries:
        rid, where = e.get("receipt", "?"), f"ledger seq {e.get('seq')}"
        if e.get("prev_hash") != prev:
            bad.append(f"{where}: chain broken (prev_hash does not match the entry before it)")
        f = files.get(rid)
        if f is None:
            bad.append(f"{where}: receipt {rid} named in the ledger has no file")
        else:
            receipt = json.loads(f.read_text())
            if f.parent.name != receipt.get("capability") or e.get("capability") != f.parent.name:
                bad.append(f"{where}: {rid} filed under the wrong capability")
            if compute_hash(e.get("prev_hash", ""), KIND, receipt) != e.get("hash"):
                bad.append(f"{where}: {rid} was edited after it was recorded (hash mismatch)")
        if not _verify_sig(pub_hex, str(e.get("hash", "")).encode(), e.get("signature") or ""):
            bad.append(f"{where}: signature does not verify against receipts.pub")
        if rid in seen:
            bad.append(f"{where}: {rid} recorded twice")
        seen.add(rid)
        prev = e.get("hash", "")
    for rid, f in sorted(files.items()):
        if rid not in seen:
            bad.append(f"{f.relative_to(runs.parent)}: a receipt file that is not in the ledger")
    return bad


def _jsonl(b: bytes) -> list[dict]:
    lines = b.decode(errors="replace").splitlines()
    return [json.loads(x) for x in lines if x.strip().startswith("{")]


def _tally(items) -> dict:
    out: dict[str, int] = {}
    for i in items:
        out[str(i)] = out.get(str(i), 0) + 1
    return dict(sorted(out.items()))


# Counts are DERIVED from the tool's own output, never typed in. One small reader per report
# format; a capability without one records hashes only. (Tool knowledge lives here in scripts/,
# never in the core.) Each takes (report bytes, stdout bytes).
def _semgrep(r: bytes, o: bytes) -> dict:
    d = json.loads(r)
    return {"results": len(d["results"]), "errors": len(d["errors"]),
            "by_severity": _tally(x["extra"]["severity"] for x in d["results"])}


def _gitleaks(r: bytes, o: bytes) -> dict:
    d = json.loads(r or b"[]")
    return {"findings": len(d), "by_rule": _tally(x["RuleID"] for x in d)}


def _trufflehog(r: bytes, o: bytes) -> dict:
    d = [x for x in _jsonl(o) if "DetectorName" in x]
    return {"findings": len(d), "verified": sum(1 for x in d if x.get("Verified"))}


def _trivy(r: bytes, o: bytes) -> dict:
    vulns = [v for t in json.loads(r).get("Results", []) for v in t.get("Vulnerabilities") or []]
    return {"vulnerabilities_by_severity": _tally(v["Severity"] for v in vulns)}


def _osv(r: bytes, o: bytes) -> dict:
    pkgs = [p for x in json.loads(r).get("results", []) for p in x.get("packages", [])]
    return {"vulnerable_packages": sum(1 for p in pkgs if p.get("vulnerabilities")),
            "vulnerabilities": sum(len(p.get("vulnerabilities", [])) for p in pkgs)}


def _nuclei(r: bytes, o: bytes) -> dict:
    """With -ms every template's result is a line (matched or not) and carries the response,
    so we can say how many answers came from the app and how many from an edge challenge."""
    d = _jsonl(r)
    hit = [x for x in d if x.get("matcher-status", True)]
    resp = [x.get("response") or "" for x in d]
    challenged = sum(1 for t in resp if "security checkpoint" in t.lower()
                     or "x-vercel-mitigated: challenge" in t.lower())
    return {"results": len(d), "matches": len(hit),
            "matches_by_severity": _tally(x["info"]["severity"] for x in hit),
            "matched_templates": _tally(x["template-id"] for x in hit),
            "responses_by_status": _tally(t.split(" ", 2)[1] if t.startswith("HTTP/") else "none"
                                          for t in resp),
            "edge_challenged": challenged}


def _skillspector(r: bytes, o: bytes) -> dict:
    """The per-skill wrapper's combined array: [{skill, exit, risk_severity, findings, ...}]."""
    d = json.loads(r)
    scanned = [x for x in d if x.get("risk_severity")]
    return {"skills": len(d), "scanned": len(scanned),
            "not_scanned": sorted(x["skill"] for x in d if not x.get("risk_severity")),
            "by_risk": _tally(x["risk_severity"] for x in scanned),
            "findings": sum(x.get("findings", 0) for x in scanned)}


PARSERS = {"semgrep": _semgrep, "gitleaks": _gitleaks, "trufflehog": _trufflehog,
           "trivy": _trivy, "osv-scanner": _osv, "nuclei": _nuclei,
           "skillspector": _skillspector}


def derive_counts(cap_id: str, report: bytes, stdout: bytes) -> dict:
    parse = PARSERS.get(cap_id)
    if parse is None:
        return {}
    try:
        return parse(report, stdout)
    except (ValueError, KeyError, TypeError, AttributeError) as e:
        return {"parse_error": f"{type(e).__name__}: {e}"}


def _base(args, cap) -> dict:
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    slug = args.target.split("@")[0].rstrip("/").split("/")[-1].lower() or "target"
    return {
        "id": f"{now:%Y%m%dT%H%M%SZ}-{args.capability}-{slug}-{args.phase}",
        "capability": args.capability,
        "tool_version": args.tool_version,
        "target": args.target,
        "phase": args.phase,
        "ran_at": now.isoformat(),
        "controls": list(cap.covers),
        "summary": args.summary,
        "operator_notes": json.loads(args.notes) if args.notes else {},
        "triage": args.triage,
    }


def _check_target(target: str) -> None:
    import re

    if not re.fullmatch(r"[\w.-]+/[\w.-]+@[0-9a-f]{40}|https://[^\s]+|~?/[^\s]+", target):
        raise SystemExit(f"--target {target!r}: want owner/repo@<40-hex sha>, an https URL "
                         "or a path")


def _cap(cap_id: str):
    cap = next((c for c in load_spec().capabilities if c.id == cap_id), None)
    if cap is None:
        raise SystemExit(f"{cap_id!r} is not in data/registry.yml — register it before running it")
    if cap.pointer_only:
        raise SystemExit(f"{cap_id}: licence unconfirmed — pointer only, never run here")
    return cap


def _display(cmd: list[str], redact: list[str]) -> str:
    text = " ".join(cmd)
    for pair in redact:
        path, _, label = pair.partition("=")
        text = text.replace(path, label)
    return text.replace(str(Path.home()), "~")


def cmd_run(args) -> int:
    _check_target(args.target)
    cap = _cap(args.capability)
    if not args.cmd:
        raise SystemExit("nothing to run: pass the command after --")
    t0 = time.monotonic()
    p = subprocess.run(args.cmd, cwd=args.cwd, capture_output=True)
    receipt = _base(args, cap)
    result = GateResult.from_exit_code(cap.id, p.returncode, summary=args.summary,
                                       controls=list(cap.covers))
    report = Path(args.report).read_bytes() if args.report else b""
    receipt.update({
        "counts": derive_counts(cap.id, report, p.stdout),
        "observed": "local",
        "ran_on": f"{platform.system().lower()}-{platform.machine()}",
        "command": _display(args.cmd, args.redact),
        "exit_code": p.returncode,
        "verdict": result.verdict.value,
        "duration_s": round(time.monotonic() - t0, 1),
        "stdout_sha256": sha256_bytes(p.stdout),
        "stderr_sha256": sha256_bytes(p.stderr),
        "report_sha256": sha256_bytes(report) if args.report else "",
    })
    out = append(receipt, runs=RUNS, signer=load_signer(DEFAULT_KEY, RUNS))
    print(f"receipt: {out.relative_to(ROOT)}  exit={p.returncode}  verdict={result.verdict.value}"
          f"  counts={json.dumps(receipt['counts'])}")
    return 0


def cmd_record(args) -> int:
    _check_target(args.target)
    cap = _cap(args.capability)
    receipt = _base(args, cap)
    result = GateResult.from_exit_code(cap.id, args.exit_code, summary=args.summary,
                                       controls=list(cap.covers))
    report = Path(args.report).read_bytes() if args.report else b""
    receipt.update({
        "counts": derive_counts(cap.id, report, b""),
        "observed": "remote",
        "ran_on": args.ran_on,
        "evidence_url": args.evidence_url,
        "command": args.command,
        "exit_code": args.exit_code,
        "verdict": result.verdict.value,
        "report_sha256": sha256_file(Path(args.report)) if args.report else "",
    })
    out = append(receipt, runs=RUNS, signer=load_signer(DEFAULT_KEY, RUNS))
    print(f"receipt: {out.relative_to(ROOT)}  exit={args.exit_code}  (observed remotely)")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="mode", required=True)
    for name in ("run", "record"):
        s = sub.add_parser(name)
        s.add_argument("--capability", required=True)
        s.add_argument("--target", required=True, help="owner/repo@sha or a URL")
        s.add_argument("--tool-version", required=True)
        s.add_argument("--phase", default="after", choices=["before", "after", "once"])
        s.add_argument("--summary", default="")
        s.add_argument("--notes", default="", help="JSON the operator adds; kept apart from counts")
        s.add_argument("--triage", default="")
        s.add_argument("--report", default="")
    run = sub.choices["run"]
    run.add_argument("--cwd", default=None)
    run.add_argument("--redact", action="append", default=[], help="PATH=LABEL in the command")
    run.add_argument("cmd", nargs=argparse.REMAINDER)
    rec = sub.choices["record"]
    rec.add_argument("--exit-code", type=int, required=True)
    rec.add_argument("--ran-on", required=True)
    rec.add_argument("--evidence-url", required=True)
    rec.add_argument("--command", default="")
    sub.add_parser("verify")
    args = ap.parse_args(argv)
    if args.mode == "run":
        if args.cmd and args.cmd[0] == "--":
            args.cmd = args.cmd[1:]
        return cmd_run(args)
    if args.mode == "record":
        return cmd_record(args)
    problems = verify()
    if problems:
        print("RECEIPT FAILURES:", file=sys.stderr)
        for p in problems:
            print(f"  ✗ {p}", file=sys.stderr)
        return 1
    n = len(_entries(RUNS))
    print(f"receipts: ok — {n} receipt(s), chain intact, every signature verifies"
          if n else "receipts: none recorded yet (nothing claimed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
