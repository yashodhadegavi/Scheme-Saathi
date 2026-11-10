"""Rule-based eligibility engine.

Eligibility is decided here, in plain code, from facts the person gave - never by a language
model. That keeps answers reproducible and auditable, and prevents invented rules.

Each condition evaluates to True / False / None (unknown). A scheme is:
  * not_eligible - at least one condition is False
  * eligible     - every condition is True
  * unknown      - otherwise (we still need information)
  * check        - (final stage only) some facts stayed unknown because the person was unsure

Condition types (see data/schemes.json):
  age_between  min <= value <= max (inclusive)
  is_true / is_false   yes/no facts
  num_lte      value <= max            (e.g. family income)
  num_gte      value >= min            (e.g. marks), optionally with a lower ``relaxed_min``
               that applies if any slot in ``relax_if_any`` is True (e.g. 50 instead of 55 for SC/ST)
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .config import SCHEMES_FILE

UNSURE = "unsure"

# Order in which missing facts are asked. Facts that unlock more schemes come first, and a
# gate question (e.g. "is there a student?") comes before the details it unlocks.
SLOT_ORDER = [
    "age",
    "has_bank_account",
    "owns_farmland",
    "self_income_tax_payer",
    "family_income_tax_payer",
    "govt_pension_10k",
    "higher_status_member",
    "lives_in_city",
    "owns_pucca_house",
    "pmjay_group",
    "has_student",
    "student_class8_govt",
    "student_post_matric",
    "annual_income",
    "student_is_sc",
    "student_is_st",
    "marks_percent",
]
NUMERIC_SLOTS = {"age", "annual_income", "marks_percent"}

TOPICS = ("farm", "pension", "housing", "health", "scholarship")

ELIGIBLE, NOT_ELIGIBLE, UNKNOWN, CHECK = "eligible", "not_eligible", "unknown", "check"


@dataclass(frozen=True)
class Condition:
    id: str
    type: str
    slot: str
    fail: dict[str, str]
    min: int | None = None
    max: int | None = None
    relaxed_min: int | None = None
    relax_if_any: tuple[str, ...] = ()

    def all_slots(self) -> tuple[str, ...]:
        return (self.slot, *self.relax_if_any)

    def check(self, facts: dict) -> tuple[bool | None, list[str]]:
        """Return (result, slots we still need to ask). UNSURE slots are never 'needed'."""
        v = facts.get(self.slot)
        if v is None:
            return None, [self.slot]
        if v == UNSURE:
            return None, []
        t = self.type
        if t == "age_between":
            return self.min <= v <= self.max, []
        if t == "is_true":
            return v is True, []
        if t == "is_false":
            return v is False, []
        if t == "num_lte":
            return v <= self.max, []
        if t == "num_gte":
            if v >= self.min:
                return True, []
            if self.relaxed_min is None or v < self.relaxed_min:
                return False, []
            vals = [facts.get(s) for s in self.relax_if_any]
            if any(x is True for x in vals):
                return True, []
            if vals and all(x is False for x in vals):
                return False, []
            return None, [s for s, x in zip(self.relax_if_any, vals) if x is None]
        raise ValueError(f"Unknown condition type: {t}")


@dataclass(frozen=True)
class Scheme:
    id: str
    topic: str
    name: dict[str, str]
    source: str
    conditions: tuple[Condition, ...]
    benefit: dict[str, str]
    documents: dict[str, list[str]]
    apply: dict[str, str]
    note: dict[str, str] = field(default_factory=dict)


@dataclass
class SchemeResult:
    scheme: Scheme
    status: str
    failed: list[Condition] = field(default_factory=list)
    missing_slots: list[str] = field(default_factory=list)  # never answered
    unsure_slots: list[str] = field(default_factory=list)   # person said "not sure"


def load_schemes(path: str | Path | None = None, topics: set[str] | None = None) -> list[Scheme]:
    data = json.loads(Path(path or SCHEMES_FILE).read_text(encoding="utf-8"))
    out = []
    for s in data["schemes"]:
        if topics is not None and s["topic"] not in topics:
            continue
        conds = tuple(
            Condition(
                id=c["id"], type=c["type"], slot=c["slot"], fail=c["fail"],
                min=c.get("min"), max=c.get("max"), relaxed_min=c.get("relaxed_min"),
                relax_if_any=tuple(c.get("relax_if_any", ())),
            )
            for c in s["conditions"]
        )
        out.append(
            Scheme(
                id=s["id"], topic=s["topic"], name=s["name"], source=s["source"], conditions=conds,
                benefit=s["benefit"], documents=s["documents"], apply=s["apply"], note=s.get("note", {}),
            )
        )
    return out


def evaluate(facts: dict, schemes: list[Scheme], final: bool = False) -> list[SchemeResult]:
    results = []
    for sc in schemes:
        failed, missing, unsure, all_true = [], [], [], True
        for c in sc.conditions:
            r, needs = c.check(facts)
            if r is False:
                failed.append(c)
                all_true = False
            elif r is None:
                all_true = False
                missing.extend(needs)
                if not needs:  # nothing left to ask: the person said "not sure"
                    unsure.extend(s for s in c.all_slots() if facts.get(s) == UNSURE)
        if failed:
            status = NOT_ELIGIBLE
            missing, unsure = [], []  # no point asking more about a scheme already ruled out
        elif all_true:
            status = ELIGIBLE
        else:
            status = CHECK if final else UNKNOWN
        results.append(SchemeResult(sc, status, failed, _uniq(missing), _uniq(unsure)))
    return results


def next_slot(results: list[SchemeResult]) -> str | None:
    """The most useful fact still missing across all schemes that are not yet decided."""
    needed = {s for r in results if r.status == UNKNOWN for s in r.missing_slots}
    for slot in SLOT_ORDER:
        if slot in needed:
            return slot
    return None


def _uniq(xs: list[str]) -> list[str]:
    seen, out = set(), []
    for x in xs:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out
