from scheme_saathi.dialogue import Dialogue
from scheme_saathi.engine import CHECK, ELIGIBLE, NOT_ELIGIBLE, UNSURE


LEGACY = {"farm", "pension"}  # the original four schemes; keeps these flow tests short


def run(lang, answers, topics=LEGACY):
    d = Dialogue(lang, topics=topics)
    r = d.start()
    for a in answers:
        r = d.handle(a)
    return d, r


def statuses(r):
    return {x.scheme.id: x.status for x in r.results}


def test_english_full_flow_all_eligible():
    d, r = run("en-IN", ["I am 35 years old and I have 2 acres of land", "yes", "no", "no", "no", "no"])
    assert r.done and statuses(r) == {k: ELIGIBLE for k in ("pm_kisan", "apy", "pmjjby", "pmsby")}


def test_telugu_flow_with_digits_and_words():
    d, r = run("te-IN", ["ముప్పై ఐదు", "అవును", "అవును", "లేదు", "లేదు", "లేదు", "లేదు"])
    assert r.done and statuses(r)["pm_kisan"] == ELIGIBLE


def test_kannada_flow():
    d, r = run("kn-IN", ["ಮೂವತ್ತೈದು", "ಹೌದು", "ಹೌದು", "ಇಲ್ಲ", "ಇಲ್ಲ", "ಇಲ್ಲ", "ಇಲ್ಲ"])
    assert r.done and set(statuses(r).values()) == {ELIGIBLE}


def test_kannada_free_utterance_skips_questions():
    d = Dialogue("kn-IN", topics=LEGACY); d.start()
    r = d.handle("ನನಗೆ ಎರಡು ಎಕರೆ ಜಮೀನು ಇದೆ, ನನ್ನ ವಯಸ್ಸು 40 ವರ್ಷ")
    assert d.facts == {"age": 40, "owns_farmland": True} and r.asked == "has_bank_account"


def test_hindi_taxpayer_flow():
    d, r = run("hi-IN", ["पैंतीस", "हाँ", "नहीं", "हां जी"])
    s = statuses(r)
    assert r.done and s["apy"] == NOT_ELIGIBLE and s["pmjjby"] == ELIGIBLE and s["pm_kisan"] == NOT_ELIGIBLE


def test_start_asks_age_first_with_greeting():
    r = Dialogue("en-IN", topics=LEGACY).start()
    assert r.asked == "age" and "Scheme Saathi" in r.text


def test_reprompt_then_gives_up_as_unsure():
    d = Dialogue("en-IN", topics=LEGACY); d.start()
    r1 = d.handle("banana"); assert r1.asked == "age" and "35" not in r1.text and not r1.done
    d.handle("banana")
    r3 = d.handle("banana")  # third failure -> unsure, moves on
    assert d.facts["age"] == UNSURE and r3.asked == "has_bank_account"


def test_volunteered_info_does_not_count_as_failure():
    d = Dialogue("en-IN", topics=LEGACY); d.start()
    r = d.handle("I have a bank account and 3 acres of land")
    assert d.facts["has_bank_account"] is True and d.facts["owns_farmland"] is True
    assert d.retries == 0 and r.asked == "age"


def test_yes_with_other_info_is_not_misread_as_answer():
    d = Dialogue("en-IN", topics=LEGACY); d.start()
    d.handle("40"); d.handle("yes"); d.handle("yes")      # age, bank, land
    assert d.asked == "self_income_tax_payer"
    d.handle("yes I have a bank account")                   # volunteers other info; must not mean "taxpayer = yes"
    assert d.facts.get("self_income_tax_payer") is None


def test_unsure_answers_end_in_check_status_not_a_wrong_yes_or_no():
    d, r = run("en-IN", ["35", "yes", "yes", "no", "not sure", "no", "no"])
    s = statuses(r)
    assert r.done and s["pm_kisan"] == CHECK and s["apy"] == ELIGIBLE


def test_empty_input_is_handled():
    d = Dialogue("en-IN", topics=LEGACY); d.start()
    r = d.handle("")
    assert "couldn't hear" in r.text and r.asked == "age"


def test_after_done_new_input_does_not_crash():
    d, r = run("en-IN", ["15", "no"])
    assert r.done
    assert d.handle("hello").done


def test_corrections_recompute():
    d, r = run("en-IN", ["35", "yes", "no", "no"])
    assert statuses(r)["apy"] == ELIGIBLE
    r2 = d.apply_corrections({"age": 45})
    assert r2.done and statuses(r2)["apy"] == NOT_ELIGIBLE
    r3 = d.apply_corrections({"has_bank_account": None})
    assert not r3.done and r3.asked == "has_bank_account"


def test_summary_text_has_no_digits_for_clean_tts():
    d, r = run("en-IN", ["35", "yes", "yes", "no", "no", "no", "no"])
    assert not any(ch.isdigit() for ch in r.speech)
    for lang, ans in (("hi-IN", ["पैंतीस", "हाँ", "हाँ", "नहीं", "नहीं", "नहीं", "नहीं"]),
                      ("te-IN", ["ముప్పై ఐదు", "అవును", "అవును", "లేదు", "లేదు", "లేదు", "లేదు"]),
                      ("kn-IN", ["ಮೂವತ್ತೈದು", "ಹೌದು", "ಹೌದು", "ಇಲ್ಲ", "ಇಲ್ಲ", "ಇಲ್ಲ", "ಇಲ್ಲ"])):
        _, rr = run(lang, ans)
        assert rr.done and not any(ch.isdigit() for ch in rr.speech)


def test_all_questions_free_of_digits():
    from scheme_saathi import i18n
    for slot, by_lang in i18n.QUESTIONS.items():
        for lang, text in by_lang.items():
            assert not any(ch.isdigit() for ch in text), (slot, lang)


# ----------------------------------------------------------------------------------------------
# Housing / health / scholarships
# ----------------------------------------------------------------------------------------------
def drive(lang, by_slot, topics=None, first=None):
    """Answer each question by its slot name, so tests do not depend on question order."""
    d = Dialogue(lang, topics=topics)
    r = d.start()
    if first:
        r = d.handle(first)
    asked = []
    for _ in range(40):
        if r.done:
            break
        asked.append(d.asked)
        r = d.handle(by_slot[d.asked])
    assert r.done, asked
    return d, r, asked


BASE = dict(age="35", has_bank_account="yes", owns_farmland="no", self_income_tax_payer="no",
            family_income_tax_payer="no", govt_pension_10k="no", higher_status_member="no",
            lives_in_city="yes", owns_pucca_house="no", annual_income="2 lakh", pmjay_group="no",
            has_student="no", student_class8_govt="no", student_post_matric="yes", student_is_sc="yes",
            student_is_st="no", marks_percent="60")


def test_full_run_urban_family_no_student():
    d, r, asked = drive("en-IN", BASE)
    s = statuses(r)
    assert s["pmay_u"] == ELIGIBLE and s["pmay_g"] == NOT_ELIGIBLE and s["pmjay_family"] == NOT_ELIGIBLE
    assert s["nmmss"] == NOT_ELIGIBLE and s["pms_sc"] == NOT_ELIGIBLE and s["pmjay_70"] == NOT_ELIGIBLE
    assert "student_class8_govt" not in asked and "marks_percent" not in asked


def test_rural_no_student_never_asks_for_income():
    d, r, asked = drive("en-IN", {**BASE, "lives_in_city": "no", "owns_farmland": "no"})
    assert "annual_income" not in asked and statuses(r)["pmay_g"] == ELIGIBLE


def test_post_matric_sc_student_flow():
    d, r, asked = drive("en-IN", {**BASE, "has_student": "yes"})
    assert statuses(r)["pms_sc"] == ELIGIBLE and "marks_percent" not in asked


def test_class8_student_flow_with_marks_and_income_spoken_naturally():
    d, r, asked = drive("en-IN", {**BASE, "has_student": "yes", "student_class8_govt": "yes",
                                  "annual_income": "three lakh", "marks_percent": "52 percent"})
    assert statuses(r)["nmmss"] == ELIGIBLE        # 52 is enough because the student is SC
    d, r, _ = drive("en-IN", {**BASE, "has_student": "yes", "student_class8_govt": "yes",
                              "marks_percent": "52", "student_is_sc": "no"})
    assert statuses(r)["nmmss"] == NOT_ELIGIBLE


def test_monthly_income_is_converted_to_yearly():
    d, r, _ = drive("en-IN", {**BASE, "annual_income": "ten thousand per month"}, topics={"housing"})
    assert d.facts["annual_income"] == 120000


def test_income_reprompt_then_accept():
    d = Dialogue("en-IN", topics={"housing"}); d.start()
    d.handle("35"); d.handle("yes")                      # age (not needed) -> city
    d = Dialogue("en-IN", topics={"housing"}); d.start()
    d.handle("yes"); d.handle("no")                      # city, no pucca house
    assert d.asked == "annual_income"
    r = d.handle("three")                                # ambiguous: re-ask with an example
    assert "lakh" in r.text and d.asked == "annual_income"
    r = d.handle("3 lakh")
    assert d.facts["annual_income"] == 300000 and r.done


def test_topics_limit_the_questions():
    d, r, asked = drive("en-IN", BASE, topics={"housing"})
    assert asked == ["lives_in_city", "owns_pucca_house", "annual_income"]
    assert {x.scheme.id for x in r.results} == {"pmay_u", "pmay_g"}


def test_bad_topics_raise():
    import pytest
    with pytest.raises(ValueError):
        Dialogue("en-IN", topics={"nonsense"})


def test_village_word_in_free_speech_is_understood():
    d = Dialogue("en-IN", topics={"housing"}); d.start()
    r = d.handle("I live in a village")
    assert d.facts == {"lives_in_city": False} and r.asked == "owns_pucca_house"


def test_kannada_housing_and_health_flow():
    by = {"age": "ನಲವತ್ತು", "lives_in_city": "ಹೌದು", "owns_pucca_house": "ಇಲ್ಲ", "annual_income": "ಎರಡು ಲಕ್ಷ", "pmjay_group": "ಹೌದು"}
    d, r, asked = drive("kn-IN", by, topics={"housing", "health"})
    s = statuses(r)
    assert s["pmay_u"] == ELIGIBLE and s["pmjay_family"] == ELIGIBLE and not any(ch.isdigit() for ch in r.speech)


def test_telugu_and_hindi_income_flows():
    d, r, _ = drive("te-IN", {"lives_in_city": "అవును", "owns_pucca_house": "లేదు", "annual_income": "రెండు లక్షలు"}, topics={"housing"})
    assert statuses(r)["pmay_u"] == ELIGIBLE
    d, r, _ = drive("hi-IN", {"lives_in_city": "हाँ", "owns_pucca_house": "नहीं", "annual_income": "बीस हज़ार महीने"}, topics={"housing"})
    assert d.facts["annual_income"] == 240000 and statuses(r)["pmay_u"] == ELIGIBLE


def test_spoken_summary_skips_not_eligible_list_but_screen_text_has_it():
    d, r, _ = drive("en-IN", BASE)
    assert "do not seem to qualify" in r.text and "do not seem to qualify" not in r.speech


def test_all_questions_and_summaries_have_no_digits_in_every_language():
    from scheme_saathi import i18n
    for slot, by_lang in i18n.QUESTIONS.items():
        for lang, text in by_lang.items():
            assert not any(ch.isdigit() for ch in text), (slot, lang)
    for key in ("reprompt_income", "reprompt_marks", "reprompt_age", "reprompt_yn"):
        for lang, text in i18n.MESSAGES[key].items():
            assert not any(ch.isdigit() for ch in text), (key, lang)
    for lang, ans in (("hi-IN", "हाँ"), ("te-IN", "అవును"), ("kn-IN", "ಹೌದು")):
        names = [sc.name[lang[:2]] for sc in Dialogue(lang).schemes]
        assert not any(ch.isdigit() for n in names for ch in n), (lang, names)
