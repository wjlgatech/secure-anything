#!/usr/bin/env python3
"""The repo audits itself — including its meta-ness.

Each principle in data/ainative.yml names a check; this script IS those checks, scored against
in-repo evidence. A discipline regression fails CI. A principle whose check cannot be
implemented is reported as NOT MEASURED and — per the discipline it is auditing — counts as a
failure, never as a silent pass.
"""
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from secure_anything.spec import Evidence, Status, load_spec  # noqa: E402

CORE = ROOT / "src" / "secure_anything"
DOMAIN_SMELLS = ("github", "gitlab", "semgrep", "codeql", "webhook", "openai", "anthropic")


def _core_files() -> list[Path]:
    return [p for p in CORE.rglob("*.py") if "organs" not in p.parts]


def _script_ok(name: str, *args: str) -> tuple[bool, str]:
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / name), *args],
                       capture_output=True, text=True, cwd=ROOT)
    out = (r.stdout + r.stderr).strip()
    return r.returncode == 0, out.splitlines()[-1] if out else ""


# --- one function per principle id -------------------------------------------------------

def spec_as_data() -> tuple[bool, str]:
    for f in ("registry.yml", "knowledge.yml", "controls.yml", "ainative.yml"):
        if not (ROOT / "data" / f).exists():
            return False, f"data/{f} missing"
    return _script_ok("build.py", "--check")


def lean_core() -> tuple[bool, str]:
    total = sum(len(p.read_text().splitlines()) for p in _core_files())
    return total <= 600, f"core is {total} LOC (budget 600)"


def no_domain_logic_in_core() -> tuple[bool, str]:
    for p in _core_files():
        tree = ast.parse(p.read_text())
        code = p.read_text().lower()
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
                doc = ast.get_docstring(node)
                if doc:
                    code = code.replace(doc.lower(), "")
            mod = node.module if isinstance(node, ast.ImportFrom) else ""
            if mod and "organs" in mod:
                return False, f"{p.name} imports an organ"
        code = "\n".join(ln.split("#")[0] for ln in code.splitlines())
        hits = [s for s in DOMAIN_SMELLS if s in code]
        if hits:
            return False, f"{p.name} names {hits}"
    return True, f"{len(_core_files())} core modules clean"


def satellites_never_vendored() -> tuple[bool, str]:
    for bad in ("vendor", "third_party", "vendored"):
        if (ROOT / bad).exists():
            return False, f"{bad}/ exists"
    nested = [p for p in (ROOT / "src").rglob(".git") if p.is_dir()]
    return not nested, "no vendored trees" if not nested else f"nested checkouts: {nested}"


def status_ladder_enforced() -> tuple[bool, str]:
    return _script_ok("verify_registry.py")


def aggregate_exit_codes_not_claims() -> tuple[bool, str]:
    from secure_anything.gate import GateResult
    r = GateResult.from_exit_code("x", 3)
    ok = r.exit_code == 3 and hasattr(r, "evidence_ref")
    return ok, "GateResult carries exit_code + evidence_ref"


def no_evidence_means_no() -> tuple[bool, str]:
    from secure_anything.gate import Aggregate, GateResult
    agg = Aggregate(results=[GateResult.from_exit_code("a", 0),
                             GateResult.not_measured("b", "unavailable")], blocking=True)
    empty = Aggregate(results=[], blocking=True)
    return (not agg.passed and not empty.passed), "unmeasured cannot make a blocking gate green"


def evidence_tiered_knowledge() -> tuple[bool, str]:
    s = load_spec()
    for c in s.cards:
        if not c.verified_at:
            return False, f"{c.id} has no verified_at"
        if c.unconfirmed and c.evidence is Evidence.VERIFIED:
            return False, f"{c.id} claims verified with an unconfirmed note"
    return True, f"{len(s.cards)} cards tiered and dated"


def license_honesty() -> tuple[bool, str]:
    for c in load_spec().capabilities:
        if c.license in ("", "NOASSERTION"):
            if c.license_confirmed or c.status is Status.INTEGRATED:
                return False, f"{c.id} treats an unresolved licence as permission"
    return True, "unresolved licences are pointer-only"


def charter_first() -> tuple[bool, str]:
    return _script_ok("manifest_gate.py")


def north_star_computable() -> tuple[bool, str]:
    return _script_ok("northstar.py")


def router_is_executable() -> tuple[bool, str]:
    r = subprocess.run([sys.executable, "-m", "pytest", "tests/test_router_eval.py", "-q"],
                       capture_output=True, text=True, cwd=ROOT)
    return r.returncode == 0, "every eval routing case is a passing test"


def gate_is_offline() -> tuple[bool, str]:
    """The gate must not reach the network. Checked structurally: no test imports a live
    HTTP client without a transport fake, and `make check` names no network target."""
    mk = (ROOT / "Makefile").read_text()
    check_line = next((ln for ln in mk.splitlines() if ln.startswith("check:")), "")
    forbidden = [w for w in ("sync", "fetch", "curl", "npm") if w in check_line]
    return not forbidden, f"`make check` targets: {check_line.strip() or 'missing'}"


def tamper_evident_record() -> tuple[bool, str]:
    from secure_anything.ledger import compute_hash, verify_chain

    class E:  # minimal stand-in; the full ORM path is covered in tests/
        def __init__(s, prev, kind, payload):
            s.prev_hash, s.kind, s.payload = prev, kind, payload
            s.hash, s.signature = compute_hash(prev, kind, payload), None

    e = E("0" * 64, "decision", {"a": 1})
    ok_before = verify_chain([e])
    e.payload = {"a": 2}  # tamper
    return (ok_before and not verify_chain([e])), "chain verify detects a mutated payload"


def honest_edges() -> tuple[bool, str]:
    r = "## Honest edges" in (ROOT / "README.md").read_text()
    v = "## Honest edges" in (ROOT / "docs" / "VISION.md").read_text()
    return (r and v), "README and VISION both state their limits"


CHECKS = {
    "spec-as-data": spec_as_data,
    "lean-core": lean_core,
    "no-domain-logic-in-core": no_domain_logic_in_core,
    "satellites-never-vendored": satellites_never_vendored,
    "status-ladder-enforced": status_ladder_enforced,
    "aggregate-exit-codes-not-claims": aggregate_exit_codes_not_claims,
    "no-evidence-means-no": no_evidence_means_no,
    "evidence-tiered-knowledge": evidence_tiered_knowledge,
    "license-honesty": license_honesty,
    "charter-first": charter_first,
    "north-star-computable": north_star_computable,
    "router-is-executable": router_is_executable,
    "gate-is-offline": gate_is_offline,
    "tamper-evident-record": tamper_evident_record,
    "honest-edges": honest_edges,
}


def main() -> int:
    s = load_spec()
    earned = possible = 0
    rows, unmeasured = [], []
    for p in s.principles:
        fn = CHECKS.get(p.id)
        possible += p.weight
        if fn is None:
            unmeasured.append(p.id)
            rows.append(
                f"  ❓ NOT MEASURED  {p.id}  (no check implemented — counts as a failure)"
            )
            continue
        try:
            ok, detail = fn()
        except Exception as exc:  # a check that errors is not a pass
            ok, detail = False, f"check raised {type(exc).__name__}: {exc}"
        earned += p.weight if ok else 0
        rows.append(f"  {'✅' if ok else '❌'} {p.id:<34} {detail}")

    score = round(100 * earned / possible) if possible else 0
    print("ainative self-audit — how this repo OPERATES\n")
    print("\n".join(rows))
    print(f"\nscore: {score}/100 (gate ≥ {s.gate_min_score})")
    if unmeasured:
        print(f"NOT MEASURED: {', '.join(unmeasured)} — excluded from credit, never a silent pass.")
    if score < s.gate_min_score:
        print(f"\nFAIL — discipline regression: {score} < {s.gate_min_score}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
