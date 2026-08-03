"""The gate seam: every capability, ours or theirs, reduces to a comparable exit code.

Two invariants live here and are enforced by tests, not by convention:

1. **Aggregate exit codes, never claims.** A capability reports an integer exit code and a
   pointer to its evidence. Prose from a vendor is not a result.
2. **No evidence means no.** A capability we could not run is NOT_MEASURED — excluded from the
   score and reported by name. A blocking aggregate can never be green while something is
   unmeasured. Silence is not a pass.
"""
from __future__ import annotations

from enum import Enum
from typing import Protocol, runtime_checkable

from pydantic import BaseModel, Field


class Verdict(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    NOT_MEASURED = "not_measured"


class GateResult(BaseModel):
    capability: str
    verdict: Verdict
    # None when NOT_MEASURED — we never invent a 0 for something that did not run.
    exit_code: int | None = None
    summary: str = ""
    evidence_ref: str = ""  # path to a run receipt under runs/<capability>/
    controls: list[str] = Field(default_factory=list)

    @classmethod
    def from_exit_code(
        cls, capability: str, exit_code: int, *, summary: str = "",
        evidence_ref: str = "", controls: list[str] | None = None,
    ) -> GateResult:
        return cls(
            capability=capability,
            verdict=Verdict.PASS if exit_code == 0 else Verdict.FAIL,
            exit_code=exit_code,
            summary=summary,
            evidence_ref=evidence_ref,
            controls=controls or [],
        )

    @classmethod
    def not_measured(cls, capability: str, why: str, controls: list[str] | None = None):
        return cls(
            capability=capability,
            verdict=Verdict.NOT_MEASURED,
            exit_code=None,
            summary=why,
            controls=controls or [],
        )


@runtime_checkable
class GateAdapter(Protocol):
    """What an organ or a satellite wrapper must implement to be gateable."""

    id: str

    def run(self, target: str) -> GateResult: ...


class Aggregate(BaseModel):
    """The verdict over many capabilities. `blocking` is the CI-gating posture."""

    results: list[GateResult] = Field(default_factory=list)
    blocking: bool = True

    @property
    def failed(self) -> list[GateResult]:
        return [r for r in self.results if r.verdict is Verdict.FAIL]

    @property
    def unmeasured(self) -> list[GateResult]:
        return [r for r in self.results if r.verdict is Verdict.NOT_MEASURED]

    @property
    def passed(self) -> bool:
        if self.failed:
            return False
        # A blocking gate cannot go green on unmeasured items, and an aggregate with
        # nothing in it at all is not a pass — it is an absence of evidence.
        if self.blocking and (self.unmeasured or not self.results):
            return False
        return True

    @property
    def exit_code(self) -> int:
        return 0 if self.passed else 1

    def report(self) -> str:
        label = {Verdict.PASS: "PASS", Verdict.FAIL: "FAIL", Verdict.NOT_MEASURED: "NOT MEASURED"}
        lines = [
            f"{label[r.verdict]:<12} {r.capability}"
            + (f"  (exit {r.exit_code})" if r.exit_code is not None else "")
            + (f"  — {r.summary}" if r.summary else "")
            for r in self.results
        ]
        if self.unmeasured:
            lines.append(f"\n{len(self.unmeasured)} capability(ies) NOT MEASURED — excluded "
                         "from the score, never counted as a pass.")
        lines.append(f"\naggregate: {'PASS' if self.passed else 'FAIL'} (exit {self.exit_code})")
        return "\n".join(lines)
