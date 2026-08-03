"""Spec-as-data: typed loaders for data/*.yml.

The YAML files are the single source of truth. This module only *reads and types* them —
it deliberately does not check on-disk evidence (that is `scripts/verify_registry.py`,
kept independent so the maker is not the checker).
"""
from __future__ import annotations

from enum import Enum
from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


class Status(str, Enum):
    CANDIDATE = "candidate"
    DIGESTED = "digested"
    INTEGRATED = "integrated"

    @property
    def mark(self) -> str:
        return {"candidate": "⚪", "digested": "🟡", "integrated": "🟢"}[self.value]

    @property
    def rank(self) -> int:
        return {"candidate": 0, "digested": 1, "integrated": 2}[self.value]


class Evidence(str, Enum):
    VERIFIED = "verified"
    CORROBORATED = "corroborated"
    CLAIMED = "claimed"
    DISPUTED = "disputed"


class Capability(BaseModel):
    """One thing that can run: an organ (ours), a family repo, or an external satellite."""

    id: str
    kind: str  # organ | family | external
    role: str  # gate | scanner | guardrail | redteam | benchmark | policy | ...
    capability: str
    url: str
    status: Status = Status.CANDIDATE
    license: str = ""
    license_confirmed: bool = False
    pinned_sha: str = ""
    stars: int | None = None
    visibility: str = "public"
    verified_at: str = ""
    upstream_pushed_at: str = ""
    covers: list[str] = Field(default_factory=list)
    triggers: list[str] = Field(default_factory=list)
    notes: str = ""

    @property
    def pointer_only(self) -> bool:
        """Unknown license is treated as restrictive, not as permission."""
        return not self.license_confirmed


class KnowledgeCard(BaseModel):
    """One thing that can be cited: a paper, book, blog, person, lab, standard, concept."""

    id: str
    kind: str
    title: str
    url: str = ""
    by: str = ""
    year: int | None = None
    evidence: Evidence = Evidence.CLAIMED
    verified_at: str = ""
    summary: str = ""
    why_it_matters: str = ""
    canonical_for: str = ""
    unconfirmed: str = ""
    covers: list[str] = Field(default_factory=list)
    triggers: list[str] = Field(default_factory=list)

    model_config = {"extra": "allow"}  # publisher/isbn/affiliation/etc. vary by kind

    @property
    def citable_as_fact(self) -> bool:
        return self.evidence in (Evidence.VERIFIED, Evidence.CORROBORATED)


class Control(BaseModel):
    id: str
    title: str


class Framework(BaseModel):
    id: str
    title: str
    edition: str = ""
    url: str = ""
    evidence: Evidence = Evidence.CLAIMED
    verified_at: str = ""
    controls: list[Control] = Field(default_factory=list)


class Principle(BaseModel):
    id: str
    statement: str
    check: str
    weight: int = 1


class Spec(BaseModel):
    """Everything the composition layer knows, loaded once."""

    capabilities: list[Capability] = Field(default_factory=list)
    cards: list[KnowledgeCard] = Field(default_factory=list)
    frameworks: list[Framework] = Field(default_factory=list)
    principles: list[Principle] = Field(default_factory=list)
    gate_min_score: int = 90

    @property
    def controls(self) -> list[Control]:
        return [c for f in self.frameworks for c in f.controls]


def _read(path: Path) -> dict:
    return yaml.safe_load(path.read_text()) or {}


def _framework(f: dict) -> Framework:
    controls = [Control(**c) for c in f.pop("controls", [])]
    return Framework(controls=controls,
                     **{k: v for k, v in f.items() if k in Framework.model_fields})


def load_spec(data_dir: Path | None = None) -> Spec:
    d = data_dir or DATA_DIR
    frameworks = [_framework(f) for f in _read(d / "controls.yml").get("frameworks", [])]
    ain = _read(d / "ainative.yml")
    return Spec(
        capabilities=[Capability(**c) for c in _read(d / "registry.yml").get("capabilities", [])],
        cards=[KnowledgeCard(**c) for c in _read(d / "knowledge.yml").get("cards", [])],
        frameworks=frameworks,
        principles=[Principle(**p) for p in ain.get("principles", [])],
        gate_min_score=ain.get("gate_min_score", 90),
    )


@lru_cache(maxsize=1)
def spec() -> Spec:
    return load_spec()
