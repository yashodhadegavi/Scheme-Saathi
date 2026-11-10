"""Conversation manager: asks one question at a time, parses the answer, and finishes with a
summary. It never calls the network, so the whole flow is unit-testable offline."""
from __future__ import annotations

from dataclasses import dataclass, field

from . import i18n
from .config import SHORT
from .engine import (
    CHECK, ELIGIBLE, NOT_ELIGIBLE, SLOT_ORDER, UNSURE, Scheme, SchemeResult,
    evaluate, load_schemes, next_slot,
)
from .parsing import extract_facts, parse_answer
from .text_utils import norm_text, tokens

MAX_RETRIES = 2
REPROMPT = {"age": "reprompt_age", "annual_income": "reprompt_income", "marks_percent": "reprompt_marks"}


@dataclass
class Reply:
    text: str
    speech: str
    done: bool = False
    asked: str | None = None
    results: list[SchemeResult] | None = None
    noted: dict = field(default_factory=dict)


class Dialogue:
    def __init__(self, language_code: str = "en-IN", schemes: list[Scheme] | None = None,
                 topics: set[str] | frozenset[str] | list[str] | None = None):
        if language_code not in SHORT:
            raise ValueError(f"Unsupported language: {language_code}")
        self.language_code = language_code
        self.lang = SHORT[language_code]
        self.topics = frozenset(topics) if topics else None  # None = everything
        self.schemes = schemes if schemes is not None else load_schemes(
            topics=set(self.topics) if self.topics else None)
        if not self.schemes:
            raise ValueError("No schemes match the chosen topics")
        self.reset()

    # ----------------------------------------------------------------------------------------
    def reset(self) -> None:
        self.facts: dict[str, object] = {}
        self.asked: str | None = None
        self.retries = 0
        self.done = False
        self.results: list[SchemeResult] | None = None

    def _m(self, key: str, **fmt) -> str:
        return i18n.t(i18n.MESSAGES, key, self.lang, **fmt)

    def _q(self, slot: str) -> str:
        return i18n.t(i18n.QUESTIONS, slot, self.lang)

    # ----------------------------------------------------------------------------------------
    def start(self) -> Reply:
        self.reset()
        greeting = self._m("greeting")
        reply = self._advance(prefix=greeting + " ", noted={})
        return reply

    def handle(self, text: str) -> Reply:
        if self.done:
            msg = self._m("already_done")
            return Reply(msg, msg, done=True, results=self.results)
        if not norm_text(text or ""):
            msg = self._m("no_speech")
            return Reply(msg + " " + self._q(self.asked), msg + " " + self._q(self.asked), asked=self.asked) \
                if self.asked else Reply(msg, msg)

        noted: dict = {}
        asked_ok = False
        ext = extract_facts(text)

        # A long answer that volunteers *other* facts ("yes I have two acres") must not be read
        # as the yes/no for the question we asked. Short answers are always read as the answer.
        volunteers_other = any(k != self.asked for k in ext)
        short_answer = len(tokens(text)) <= 2
        if self.asked and (short_answer or not volunteers_other):
            val = parse_answer(self.asked, text)
            if val is not None:
                self.facts[self.asked] = val
                noted[self.asked] = val
                asked_ok = True

        for slot, val in ext.items():
            if slot not in self.facts or self.facts[slot] == UNSURE:
                self.facts[slot] = val
                noted[slot] = val
            if slot == self.asked:
                asked_ok = True

        prefix = ""
        if self.asked and not asked_ok:
            if noted:
                # They told us something useful; just ask again without counting a failure.
                pass
            else:
                self.retries += 1
                if self.retries > MAX_RETRIES:
                    self.facts[self.asked] = UNSURE
                    noted[self.asked] = UNSURE
                    self.retries = 0
                    prefix = self._m("gave_up") + " "
                else:
                    hint = self._m(REPROMPT.get(self.asked, "reprompt_yn"))
                    q = self._q(self.asked)
                    return Reply(hint + " " + q, hint + " " + q, asked=self.asked, noted=noted)
        else:
            self.retries = 0
        return self._advance(prefix=prefix, noted=noted)

    # ----------------------------------------------------------------------------------------
    def apply_corrections(self, corrections: dict[str, object]) -> Reply:
        """Manually set/clear facts (the "fix a wrong answer" panel) and re-evaluate."""
        for slot, val in corrections.items():
            if slot not in SLOT_ORDER:
                raise KeyError(f"Unknown slot: {slot}")
            if val is None:
                self.facts.pop(slot, None)
            else:
                self.facts[slot] = val
        self.done = False
        self.results = None
        self.retries = 0
        return self._advance(prefix="", noted=dict(corrections))

    # ----------------------------------------------------------------------------------------
    def _advance(self, prefix: str, noted: dict) -> Reply:
        results = evaluate(self.facts, self.schemes)
        slot = next_slot(results)
        if slot is not None:
            self.asked = slot
            q = self._q(slot)
            return Reply(prefix + q, prefix + q, asked=slot, noted=noted)

        self.asked = None
        self.done = True
        self.results = evaluate(self.facts, self.schemes, final=True)
        text, speech = self.build_summary(self.results)
        return Reply(prefix + text, prefix + speech, done=True, results=self.results, noted=noted)

    def build_summary(self, results: list[SchemeResult]) -> tuple[str, str]:
        """Return (text shown on screen, text spoken). The spoken version leaves out the list of
        schemes that do not apply, to keep it short; the screen shows every card."""
        def names(status: str) -> str:
            return ", ".join(r.scheme.name[self.lang] for r in results if r.status == status)

        head = [self._m("summary_intro")]
        if any(r.status == ELIGIBLE for r in results):
            head.append(self._m("summary_eligible", names=names(ELIGIBLE)))
        else:
            head.append(self._m("summary_none"))
        if any(r.status == CHECK for r in results):
            head.append(self._m("summary_check", names=names(CHECK)))
        tail = [self._m("summary_closing")]
        not_part = [self._m("summary_not", names=names(NOT_ELIGIBLE))] if any(
            r.status == NOT_ELIGIBLE for r in results) else []
        return " ".join(head + not_part + tail), " ".join(head + tail)
