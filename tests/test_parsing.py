import pytest

from scheme_saathi.parsing import extract_facts, parse_age, parse_answer, parse_yes_no
from scheme_saathi.text_utils import norm_text


@pytest.mark.parametrize("text,expected", [
    ("Yes", "yes"), ("yeah I do", "yes"), ("no", "no"), ("I don't have one", "no"), ("not really", "no"),
    ("I have a bank account", "yes"), ("not sure", "unsure"), ("I don't know", "unsure"),
    ("हाँ", "yes"), ("हां जी", "yes"), ("नहीं", "no"), ("नहीं है", "no"), ("पता नहीं", "unsure"),
    ("haan", "yes"), ("nahi", "no"), ("pata nahi", "unsure"),
    ("అవును", "yes"), ("అవునండి", "yes"), ("ఉంది", "yes"), ("లేదు", "no"), ("లేదండి", "no"),
    ("కాదు", "no"), ("తెలియదు", "unsure"), ("avunu", "yes"), ("ledu", "no"),
    ("ಹೌದು", "yes"), ("ಇದೆ", "yes"), ("ಇಲ್ಲ", "no"), ("ಇಲ್ಲರೀ", "no"), ("ಗೊತ್ತಿಲ್ಲ", "unsure"), ("houdu", "yes"), ("illa", "no"),
    ("ಇಲ್ಲಿ", None), ("ಅಲ್ಲಿ", None),
    ("", None), ("   ", None), ("banana", None), ("లేదా", None),
])
def test_yes_no(text, expected):
    assert parse_yes_no(text) == expected


@pytest.mark.parametrize("text,expected", [
    ("35", 35), ("I am 35 years old", 35), ("im 28", 28), ("thirty five", 35), ("twenty", 20),
    ("पैंतीस", 35), ("पैंतीस साल", 35), ("२५ साल", 25), ("నా వయసు 42", 42), ("ముప్పై ఐదు", 35),
    ("ఇరవై ఒకటి", 21), ("నలభై", 40), ("ಮೂವತ್ತೈದು", 35), ("ನನ್ನ ವಯಸ್ಸು ನಲವತ್ತು", 40), ("ಇಪ್ಪತ್ತೆಂಟು ವರ್ಷ", 28), ("ಮೂವತ್ತು ಐದು", 35), ("೩೫", 35), ("age 61", 61), ("I have 2 acres and I am 40 years old", 40),
])
def test_age_direct_answer(text, expected):
    assert parse_age(text) == expected


@pytest.mark.parametrize("text", ["", "banana", "0", "500", "I have 2 acres and 3 cows", "I am 35 and have 2 acres, 40 years"])
def test_age_rejects_garbage_or_ambiguity(text):
    assert parse_age(text) is None


def test_age_strict_needs_age_word():
    assert parse_age("I have 2 acres", strict=True) is None
    assert parse_age("I am 35 and have 2 acres", strict=True) == 35


def test_extract_facts_positive():
    f = extract_facts("I am 35 years old, I have 2 acres of land and a bank account")
    assert f == {"age": 35, "owns_farmland": True, "has_bank_account": True}


def test_extract_facts_telugu_and_hindi():
    assert extract_facts("నాకు రెండు ఎకరాల పొలం ఉంది, నా వయసు 40 సంవత్సరాలు") == {"age": 40, "owns_farmland": True}
    assert extract_facts("mere paas teen acre zameen hai")["owns_farmland"] is True
    assert extract_facts("मेरे पास दो एकड़ खेत है")["owns_farmland"] is True


@pytest.mark.parametrize("text", [
    "I work on rented land", "I don't have any land", "ನನಗೆ ಜಮೀನು ಇಲ್ಲ", "ನಾನು ಗುತ್ತಿಗೆ ಜಮೀನು ಮಾಡುತ್ತೇನೆ", "मेरे पास ज़मीन नहीं है", "నాకు భూమి లేదు", "నేను కౌలుకు పొలం చేస్తాను",
])
def test_extract_never_infers_ownership_when_negated_or_tenant(text):
    assert "owns_farmland" not in extract_facts(text)


def test_extract_facts_kannada():
    assert extract_facts("ನನಗೆ ಎರಡು ಎಕರೆ ಜಮೀನು ಇದೆ, ನನ್ನ ವಯಸ್ಸು 40 ವರ್ಷ") == {"age": 40, "owns_farmland": True}


def test_parse_answer_types():
    assert parse_answer("age", "40") == 40
    assert parse_answer("age", "not sure") == "unsure"
    assert parse_answer("owns_farmland", "yes") is True
    assert parse_answer("owns_farmland", "no") is False
    assert parse_answer("owns_farmland", "dunno") is None


def test_norm_text_keeps_indic_vowel_signs():
    # \w-based cleaning would delete the matras and destroy these words
    assert norm_text("నహీం, లేదు!") == "నహీం లేదు"
    assert norm_text("हाँ।") == "हां"
    assert norm_text("35years") == "35 years"
    assert norm_text("౩౫") == "35"
