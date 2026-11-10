"""Text normalisation that is safe for Devanagari and Telugu.

Important: ``re.sub(r"[^\\w\\s]", "", text)`` is *not* safe for Indic text, because vowel signs
(matras) are combining marks that ``\\w`` does not match, so they would be deleted and words
destroyed. We therefore strip an explicit set of punctuation characters instead.
"""
from __future__ import annotations

import re
import unicodedata

_PUNCT = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~" "।॥…“”‘’‹›«»–—₹•|"
_PUNCT_TABLE = {ord(c): " " for c in _PUNCT if c != "'"}
_PUNCT_TABLE[ord("'")] = None  # "don't" -> "dont"
_PUNCT_TABLE[ord("’")] = None
_PUNCT_TABLE[ord("‘")] = None

# Devanagari (०-९) and Telugu (౦-౯) digits -> ASCII
_DIGITS = {ord(c): str(i) for i, c in enumerate("०१२३४५६७८९")}
_DIGITS.update({ord(c): str(i) for i, c in enumerate("౦౧౨౩౪౫౬౭౮౯")})
_DIGITS.update({ord(c): str(i) for i, c in enumerate("೦೧೨೩೪೫೬೭೮೯")})
_DIGITS.update({ord(c): str(i) for i, c in enumerate("٠١٢٣٤٥٦٧٨٩")})

_WS = re.compile(r"\s+")
_DIGIT_SPLIT = re.compile(r"(\d+)")


def norm_text(text: str) -> str:
    """Lower-case, NFC-normalise, map Indic digits to ASCII, drop punctuation, collapse spaces.

    Chandrabindu is folded into anusvara ("हाँ" == "हां") so both spellings match.
    """
    if not text:
        return ""
    t = unicodedata.normalize("NFC", str(text)).lower()
    t = t.translate(_DIGITS)
    t = t.replace("ँ", "ं")
    t = t.translate(_PUNCT_TABLE)
    t = _DIGIT_SPLIT.sub(r" \1 ", t)  # "35years" -> "35 years"
    return _WS.sub(" ", t).strip()


def tokens(text: str) -> list[str]:
    n = norm_text(text)
    return n.split(" ") if n else []


# Words that must match exactly even though they are Indic, because as a prefix they would
# swallow unrelated words (Kannada "ಇಲ್ಲ" = "no" is a prefix of "ಇಲ್ಲಿ" = "here").
EXACT_WORDS: set[str] = set()


def is_indic(word: str) -> bool:
    """True if the word has Devanagari, Telugu or Kannada letters (these get prefix matching)."""
    return any(
        "\u0900" <= ch <= "\u097f" or "\u0c00" <= ch <= "\u0c7f" or "\u0c80" <= ch <= "\u0cff"
        for ch in word
    )


def word_in(token: str, words: frozenset[str]) -> bool:
    """Exact match for Latin words; prefix match (len >= 3) for Indic words to absorb suffixes."""
    if token in words:
        return True
    if is_indic(token):
        for w in words:
            if w in EXACT_WORDS:
                continue
            if len(w) >= 3 and is_indic(w) and token.startswith(w):
                return True
    return False


def any_word_in(toks: list[str], words: frozenset[str]) -> bool:
    return any(word_in(t, words) for t in toks)
