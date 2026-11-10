"""Turn a transcript (typed or from Prisma STT) into structured facts.

Design rule: be conservative. When we are not sure what the person meant we return ``None``
and the dialogue asks again, rather than guessing a fact that decides eligibility.
"""
from __future__ import annotations

import re

from . import lexicon as lx
from .text_utils import any_word_in, norm_text, tokens, word_in

YES = "yes"
NO = "no"
UNSURE = "unsure"

MIN_AGE, MAX_AGE = 1, 110


# --------------------------------------------------------------------------------------------
# Yes / No
# --------------------------------------------------------------------------------------------
def parse_yes_no(text: str) -> str | None:
    """Return "yes", "no", "unsure" or None (not understood).

    Order matters: "not sure" / "pata nahi" must be caught before the plain negatives.
    """
    n = norm_text(text)
    if not n:
        return None
    padded = f" {n} "
    for phrase in lx.UNSURE_PHRASES:
        if f" {phrase} " in padded or (len(phrase) > 4 and phrase in n and not phrase.isascii()):
            return UNSURE
    toks = n.split(" ")
    if any_word_in(toks, lx.NO):
        return NO
    if any_word_in(toks, lx.YES):
        return YES
    return None


def has_negation(text: str) -> bool:
    toks = tokens(text)
    return any_word_in(toks, lx.NO) or any_word_in(toks, lx.TENANCY_WORDS)


# --------------------------------------------------------------------------------------------
# Numbers / age
# --------------------------------------------------------------------------------------------
def _number_candidates(toks: list[str]) -> list[tuple[int, int, int]]:
    """Return (value, first_token_index, last_token_index) for each number found."""
    out: list[tuple[int, int, int]] = []
    i = 0
    while i < len(toks):
        t = toks[i]
        if t.isdigit():
            out.append((int(t), i, i))
            i += 1
            continue
        if t in lx.TENS:  # "thirty" / "ముప్పై" optionally followed by a unit
            val, end = lx.TENS[t], i
            if i + 1 < len(toks) and toks[i + 1] in lx.UNITS and lx.UNITS[toks[i + 1]] <= 9:
                val += lx.UNITS[toks[i + 1]]
                end = i + 1
            out.append((val, i, end))
            i = end + 1
            continue
        if t in lx.SINGLES:
            out.append((lx.SINGLES[t], i, i))
            i += 1
            continue
        if t in lx.UNITS:  # Telugu/Kannada 1-9 on their own ("రెండు లక్షలు" = two lakh)
            out.append((lx.UNITS[t], i, i))
            i += 1
            continue
        i += 1
    return out


def _near_age_word(toks: list[str], start: int, end: int, window: int = 2) -> bool:
    lo, hi = max(0, start - window), min(len(toks), end + window + 1)
    return any(word_in(toks[j], lx.AGE_WORDS) for j in range(lo, hi) if j < start or j > end)


def parse_age(text: str, strict: bool = False) -> int | None:
    """Parse an age.

    strict=False: used when we just asked "how old are you?" - a lone number is accepted.
    strict=True : used on free speech - the number must sit next to an age word ("35 years").
    """
    toks = tokens(text)
    if not toks:
        return None
    cands = [(v, s, e) for (v, s, e) in _number_candidates(toks) if MIN_AGE <= v <= MAX_AGE]
    if not cands:
        return None
    near = [c for c in cands if _near_age_word(toks, c[1], c[2])]
    if strict:
        return near[0][0] if len(near) == 1 else None
    if len(near) == 1:
        return near[0][0]
    if len(cands) == 1:
        return cands[0][0]
    return None  # several numbers and no clear age word: ask again


# --------------------------------------------------------------------------------------------
# Percent (marks) and money (family income)
# --------------------------------------------------------------------------------------------
def parse_percent(text: str) -> int | None:
    """A whole-number percentage 1-100 ("sixty", "72 percent"). Ambiguity returns None."""
    toks = tokens(text)
    cands = [v for (v, _s, _e) in _number_candidates(toks) if 1 <= v <= 100]
    return cands[0] if len(cands) == 1 else None


_MAX_INCOME = 100_000_000  # ten crore a year: anything above is surely a mis-hearing


def parse_income(text: str) -> int | None:
    """Annual family income in rupees from speech like "2.5 lakh", "ten thousand per month",
    "250000", "दो लाख", "రెండు లక్షలు", "ಎರಡು ಲಕ್ಷ".

    A bare small number ("three") is ambiguous (3 rupees? 3 lakh?), so it returns None and the
    dialogue asks again with an example. "Per month" is multiplied by twelve.
    """
    raw = str(text or "").lower().replace("\u20b9", " ")
    raw = re.sub(r"(?<=\d),(?=\d)", "", raw)          # 2,50,000 -> 250000
    raw = re.sub(r"(\d)\s*\.\s*(\d)", r"\1 dot \2", raw)  # 2.5 -> 2 dot 5 (norm_text drops "." otherwise)
    toks = tokens(raw)
    if not toks:
        return None
    cands = _number_candidates(toks)
    # merge decimals: [2] dot [5] -> 2.5
    merged: list[tuple[float, int, int]] = []
    i = 0
    while i < len(cands):
        v, s_, e_ = cands[i]
        if i + 1 < len(cands) and cands[i + 1][1] == e_ + 2 and toks[e_ + 1] == "dot":
            frac = cands[i + 1][0]
            merged.append((v + frac / (10 ** len(str(frac))), s_, cands[i + 1][2]))
            i += 2
        else:
            merged.append((float(v), s_, e_))
            i += 1

    total, used_unit = 0.0, False
    for v, _s, e_ in merged:
        nxt = toks[e_ + 1] if e_ + 1 < len(toks) else ""
        if nxt and word_in(nxt, lx.LAKH_WORDS):
            total += v * 100_000
            used_unit = True
        elif nxt and word_in(nxt, lx.THOUSAND_WORDS):
            total += v * 1_000
            used_unit = True
    if not used_unit:
        big = [v for v, _s, _e in merged if v >= 1000]
        if len(big) != 1 or len(merged) != 1:
            return None
        total = big[0]
    if any_word_in(toks, lx.MONTH_WORDS):
        total *= 12
    income = int(round(total))
    return income if 0 < income <= _MAX_INCOME else None


# --------------------------------------------------------------------------------------------
# Free-form extraction (first utterance, or extra info volunteered mid-conversation)
# --------------------------------------------------------------------------------------------
def extract_facts(text: str) -> dict[str, object]:
    """Pull out only the facts we can read with high confidence from free speech.

    - age: needs an age word next to the number
    - owns_farmland: needs an explicit land/acre word and no negation or tenancy word
    - has_bank_account: needs both a bank word and an account word and no negation
    """
    facts: dict[str, object] = {}
    toks = tokens(text)
    if not toks:
        return facts

    age = parse_age(text, strict=True)
    if age is not None:
        facts["age"] = age

    negated = has_negation(text)
    if not negated:
        if any_word_in(toks, lx.LAND_WORDS):
            facts["owns_farmland"] = True
        if any_word_in(toks, lx.BANK_WORDS) and any_word_in(toks, lx.ACCOUNT_WORDS):
            facts["has_bank_account"] = True
        village, city = any_word_in(toks, lx.VILLAGE_WORDS), any_word_in(toks, lx.CITY_WORDS)
        if village != city:  # both or neither: do not guess
            facts["lives_in_city"] = city
    return facts


def parse_answer(slot: str, text: str) -> object | None:
    """Parse a direct answer to the question asked for ``slot``.

    Returns an int (age), True/False (yes/no), the string "unsure", or None if not understood.
    """
    if slot == "age":
        age = parse_age(text, strict=False)
        if age is not None:
            return age
        yn = parse_yes_no(text)
        return UNSURE if yn == UNSURE else None
    if slot in ("annual_income", "marks_percent"):
        val = parse_income(text) if slot == "annual_income" else parse_percent(text)
        if val is not None:
            return val
        return UNSURE if parse_yes_no(text) == UNSURE else None
    yn = parse_yes_no(text)
    if yn == YES:
        return True
    if yn == NO:
        return False
    if yn == UNSURE:
        return UNSURE
    return None
