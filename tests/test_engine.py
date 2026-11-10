import pytest

from scheme_saathi.engine import (CHECK, ELIGIBLE, NOT_ELIGIBLE, UNKNOWN, UNSURE, evaluate, load_schemes, next_slot)

SCHEMES = load_schemes(topics={"farm", "pension"})   # the original four
ALL = load_schemes()


def status(facts, final=False):
    return {r.scheme.id: r.status for r in evaluate(facts, SCHEMES, final=final)}


BASE = dict(age=35, has_bank_account=True, owns_farmland=True, self_income_tax_payer=False,
            family_income_tax_payer=False, govt_pension_10k=False, higher_status_member=False)


def test_everything_eligible():
    assert set(status(BASE).values()) == {ELIGIBLE}


@pytest.mark.parametrize("age,apy,pmjjby,pmsby", [
    (17, NOT_ELIGIBLE, NOT_ELIGIBLE, NOT_ELIGIBLE),
    (18, ELIGIBLE, ELIGIBLE, ELIGIBLE),
    (40, ELIGIBLE, ELIGIBLE, ELIGIBLE),
    (41, NOT_ELIGIBLE, ELIGIBLE, ELIGIBLE),
    (50, NOT_ELIGIBLE, ELIGIBLE, ELIGIBLE),
    (51, NOT_ELIGIBLE, NOT_ELIGIBLE, ELIGIBLE),
    (70, NOT_ELIGIBLE, NOT_ELIGIBLE, ELIGIBLE),
    (71, NOT_ELIGIBLE, NOT_ELIGIBLE, NOT_ELIGIBLE),
])
def test_age_boundaries(age, apy, pmjjby, pmsby):
    s = status({**BASE, "age": age})
    assert (s["apy"], s["pmjjby"], s["pmsby"]) == (apy, pmjjby, pmsby)


def test_no_bank_account_blocks_bank_schemes_only():
    s = status({**BASE, "has_bank_account": False})
    assert s["pm_kisan"] == ELIGIBLE
    assert {s["apy"], s["pmjjby"], s["pmsby"]} == {NOT_ELIGIBLE}


@pytest.mark.parametrize("slot", ["family_income_tax_payer", "govt_pension_10k", "higher_status_member"])
def test_pm_kisan_exclusions(slot):
    s = status({**BASE, slot: True})
    assert s["pm_kisan"] == NOT_ELIGIBLE
    assert s["apy"] == ELIGIBLE  # unaffected


def test_no_land_means_no_pm_kisan():
    assert status({**BASE, "owns_farmland": False})["pm_kisan"] == NOT_ELIGIBLE


def test_income_tax_payer_cannot_join_apy_but_can_join_insurance():
    s = status({**BASE, "self_income_tax_payer": True})
    assert s["apy"] == NOT_ELIGIBLE and s["pmjjby"] == ELIGIBLE and s["pmsby"] == ELIGIBLE


def test_unknown_until_facts_arrive_and_check_when_unsure():
    assert set(status({}).values()) == {UNKNOWN}
    facts = {**BASE, "govt_pension_10k": UNSURE}
    assert status(facts)["pm_kisan"] == UNKNOWN
    assert status(facts, final=True)["pm_kisan"] == CHECK


def test_a_definite_no_beats_unsure():
    facts = {**BASE, "govt_pension_10k": UNSURE, "family_income_tax_payer": True}
    assert status(facts, final=True)["pm_kisan"] == NOT_ELIGIBLE


def test_next_slot_order_and_short_circuit():
    assert next_slot(evaluate({}, SCHEMES)) == "age"
    assert next_slot(evaluate({"age": 35}, SCHEMES)) == "has_bank_account"
    assert next_slot(evaluate({"age": 35, "has_bank_account": True}, SCHEMES)) == "owns_farmland"
    # no land -> PM-KISAN is decided, so we must not ask about pension/status
    facts = {"age": 35, "has_bank_account": True, "owns_farmland": False}
    assert next_slot(evaluate(facts, SCHEMES)) == "self_income_tax_payer"
    facts["self_income_tax_payer"] = False
    assert next_slot(evaluate(facts, SCHEMES)) is None


def test_underage_without_land_needs_almost_nothing():
    facts = {"age": 15, "owns_farmland": False}
    assert next_slot(evaluate(facts, SCHEMES)) is None


def test_every_scheme_has_all_languages_and_a_source():
    for sc in SCHEMES:
        assert sc.source.startswith("https://")
        for lang in ("en", "hi", "te", "kn"):
            assert sc.name[lang] and sc.benefit[lang] and sc.apply[lang] and sc.documents[lang]
            for c in sc.conditions:
                assert c.fail[lang]
        assert len({len(sc.documents[l]) for l in ("en", "hi", "te", "kn")}) == 1


# ----------------------------------------------------------------------------------------------
# Housing, health, scholarships
# ----------------------------------------------------------------------------------------------
def st_all(facts, final=False):
    return {r.scheme.id: r.status for r in evaluate(facts, ALL, final=final)}


URBAN = dict(age=35, lives_in_city=True, owns_pucca_house=False, annual_income=200000)


@pytest.mark.parametrize("income,expected", [(0 + 1, ELIGIBLE), (300000, ELIGIBLE), (900000, ELIGIBLE), (900001, NOT_ELIGIBLE)])
def test_pmay_urban_income_boundary(income, expected):
    assert st_all({**URBAN, "annual_income": income})["pmay_u"] == expected


def test_pmay_urban_needs_city_and_no_pucca_house():
    assert st_all({**URBAN, "lives_in_city": False})["pmay_u"] == NOT_ELIGIBLE
    assert st_all({**URBAN, "owns_pucca_house": True})["pmay_u"] == NOT_ELIGIBLE


def test_pmay_gramin_is_the_rural_mirror():
    rural = {**URBAN, "lives_in_city": False}
    s = st_all(rural)
    assert s["pmay_g"] == ELIGIBLE and s["pmay_u"] == NOT_ELIGIBLE
    assert st_all({**rural, "owns_pucca_house": True})["pmay_g"] == NOT_ELIGIBLE
    assert st_all(URBAN)["pmay_g"] == NOT_ELIGIBLE


@pytest.mark.parametrize("age,expected", [(69, NOT_ELIGIBLE), (70, ELIGIBLE), (95, ELIGIBLE)])
def test_ayushman_vay_vandana_age_70_plus_any_income(age, expected):
    assert st_all({"age": age, "annual_income": 5_000_000})["pmjay_70"] == expected


def test_pmjay_family_depends_on_group_answer():
    assert st_all({"pmjay_group": True})["pmjay_family"] == ELIGIBLE
    assert st_all({"pmjay_group": False})["pmjay_family"] == NOT_ELIGIBLE


STUDENT8 = dict(has_student=True, student_class8_govt=True, annual_income=300000, marks_percent=60,
                student_is_sc=False, student_is_st=False)


def test_nmmss_basic_pass_and_income_boundary():
    assert st_all(STUDENT8)["nmmss"] == ELIGIBLE
    assert st_all({**STUDENT8, "annual_income": 350000})["nmmss"] == ELIGIBLE
    assert st_all({**STUDENT8, "annual_income": 350001})["nmmss"] == NOT_ELIGIBLE


@pytest.mark.parametrize("marks,sc,st,expected", [
    (55, False, False, ELIGIBLE), (54, False, False, NOT_ELIGIBLE),
    (50, True, False, ELIGIBLE), (50, False, True, ELIGIBLE), (49, True, False, NOT_ELIGIBLE),
    (52, True, False, ELIGIBLE), (52, False, False, NOT_ELIGIBLE),
])
def test_nmmss_marks_threshold_55_or_50_for_sc_st(marks, sc, st, expected):
    facts = {**STUDENT8, "marks_percent": marks, "student_is_sc": sc, "student_is_st": st}
    assert st_all(facts)["nmmss"] == expected


def test_nmmss_only_asks_sc_st_when_marks_are_in_the_grey_zone():
    # 60 marks passes for everyone, so SC/ST status is irrelevant and must not be asked
    facts = {k: v for k, v in STUDENT8.items() if k not in ("student_is_sc", "student_is_st")}
    assert st_all(facts)["nmmss"] == ELIGIBLE
    grey = {**facts, "marks_percent": 52}
    res = next(r for r in evaluate(grey, ALL) if r.scheme.id == "nmmss")
    assert res.status == UNKNOWN and set(res.missing_slots) == {"student_is_sc", "student_is_st"}


PMS = dict(has_student=True, student_class8_govt=False, student_post_matric=True, student_is_sc=True, annual_income=250000)


def test_post_matric_sc_rules():
    assert st_all(PMS)["pms_sc"] == ELIGIBLE
    assert st_all({**PMS, "annual_income": 250001})["pms_sc"] == NOT_ELIGIBLE
    assert st_all({**PMS, "student_is_sc": False})["pms_sc"] == NOT_ELIGIBLE
    assert st_all({**PMS, "student_post_matric": False})["pms_sc"] == NOT_ELIGIBLE
    assert st_all({**PMS, "student_class8_govt": True})["pms_sc"] == NOT_ELIGIBLE


def test_no_student_rules_out_both_scholarships_and_stops_questions():
    s = st_all({"has_student": False})
    assert s["nmmss"] == NOT_ELIGIBLE and s["pms_sc"] == NOT_ELIGIBLE


def test_unsure_income_gives_check_not_a_guess():
    s = st_all({**URBAN, "annual_income": UNSURE}, final=True)
    assert s["pmay_u"] == CHECK


def test_topic_filter():
    assert {s.id for s in load_schemes(topics={"housing"})} == {"pmay_u", "pmay_g"}
    assert {s.id for s in load_schemes(topics={"health"})} == {"pmjay_70", "pmjay_family"}
    assert {s.id for s in load_schemes(topics={"scholarship"})} == {"nmmss", "pms_sc"}


def test_every_scheme_complete_in_all_four_languages_and_has_topic():
    from scheme_saathi.engine import TOPICS
    for sc in ALL:
        assert sc.topic in TOPICS and sc.source.startswith("https://")
        for lang in ("en", "hi", "te", "kn"):
            assert sc.name[lang] and sc.benefit[lang] and sc.apply[lang] and sc.documents[lang]
            assert all(c.fail[lang] for c in sc.conditions)
        assert len({len(sc.documents[l]) for l in ("en", "hi", "te", "kn")}) == 1


def test_every_slot_used_by_a_scheme_has_a_question_and_label_in_all_languages():
    from scheme_saathi import i18n
    from scheme_saathi.engine import SLOT_ORDER
    used = {s for sc in ALL for c in sc.conditions for s in c.all_slots()}
    assert used <= set(SLOT_ORDER), used - set(SLOT_ORDER)
    for slot in used:
        assert set(i18n.QUESTIONS[slot]) == {"en", "hi", "te", "kn"}, slot
        assert set(i18n.SLOT_LABELS[slot]) == {"en", "hi", "te", "kn"}, slot
