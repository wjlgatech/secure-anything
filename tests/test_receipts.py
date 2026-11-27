"""Run receipts are the only thing that moves the north star — so forging one must fail.

Each test plants a specific forgery (an edited exit code, a dropped ledger line, a receipt
signed by another key, a file that never went through the ledger) and requires verify() to
name it. The last test re-verifies the real runs/ on disk, offline.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("receipt", ROOT / "scripts" / "receipt.py")
receipt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(receipt)

pytest.importorskip("cryptography")
from secure_anything.signing import Ed25519Signer  # noqa: E402


def _r(i: int, cap: str = "semgrep", code: int = 0) -> dict:
    return {"id": f"r{i}-{cap}", "capability": cap, "exit_code": code, "controls": ["LLM05"]}


@pytest.fixture
def runs(tmp_path):
    d = tmp_path / "runs"
    signer = receipt.load_signer(tmp_path / "k.pem", d)
    receipt.append(_r(1), runs=d, signer=signer)
    receipt.append(_r(2, "trivy", 1), runs=d, signer=signer)
    return d


def test_an_honest_chain_verifies(runs):
    assert receipt.verify(runs) == []


def test_editing_an_exit_code_is_caught(runs):
    f = runs / "trivy" / "r2-trivy.json"
    data = json.loads(f.read_text())
    data["exit_code"] = 0  # turn a red run green after the fact
    f.write_text(json.dumps(data))
    assert any("edited after it was recorded" in p for p in receipt.verify(runs))


def test_dropping_a_ledger_line_is_caught(runs):
    led = runs / "ledger.jsonl"
    led.write_text(led.read_text().splitlines()[1] + "\n")
    problems = receipt.verify(runs)
    assert any("chain broken" in p for p in problems)
    assert any("not in the ledger" in p for p in problems)


def test_a_receipt_dropped_in_by_hand_is_caught(runs):
    (runs / "semgrep" / "forged.json").write_text(json.dumps(_r(9)))
    assert any("not in the ledger" in p for p in receipt.verify(runs))


def test_a_second_key_cannot_extend_the_chain(runs, tmp_path):
    with pytest.raises(SystemExit):
        receipt.load_signer(tmp_path / "other.pem", runs)
    # and a ledger line signed by another key fails verification
    other = Ed25519Signer()
    receipt.append(_r(3), runs=runs, signer=other)
    assert any("signature does not verify" in p for p in receipt.verify(runs))


def test_receipts_are_append_only(runs, tmp_path):
    signer = receipt.load_signer(tmp_path / "k.pem", runs)
    with pytest.raises(SystemExit):
        receipt.append(_r(1), runs=runs, signer=signer)


def test_no_runs_claims_nothing(tmp_path):
    assert receipt.verify(tmp_path / "absent") == []


def test_the_real_receipts_on_disk_verify():
    assert receipt.verify(receipt.RUNS) == []
