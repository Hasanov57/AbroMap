from app.matching import evaluate, select_requirement
from app.models import ExamRequirement, Program, Requirement, University
from app.schemas import StudentProfile


def make_program(field="computer-science", year="2027/2028", ielts=6.5):
    university = University(id=1, slug="fixture", name="Fixture University", city="Berlin",
                            country="DE", is_demo=False, status="active", normalized_name="fixture university")
    program = Program(id=1, name="MSc", degree="master", field=field, university=university,
                      teaching_language="English", tuition_eur=None, is_demo=False,
                      data_status="verified_source")
    program.requirements = [Requirement(academic_year=year, applicant_category="international",
                                        ielts_min=ielts, status="verified_current")]
    university.programs = [program]
    return program


def profile(**kwargs):
    data = {"degree": "master", "field": "computer-science"}
    data.update(kwargs)
    return StudentProfile(**data)


def test_exact_and_related_subjects():
    exact = evaluate(profile(ielts=7), make_program())
    assert exact.subject_match == "exact"
    assert exact.checks["language"] == "met"
    related_program = make_program(field="information-systems")
    related = evaluate(profile(), related_program, subject_match="related", similarity=.9)
    assert related.subject_match == "related"
    assert "related_subject_not_admission_eligibility" in related.notes
    assert related.checks["subject"] == "related"
    assert evaluate(profile(), related_program) is None
    assert evaluate(profile(field="medicine"), make_program()) is None


def test_target_intake_and_historical_label():
    program = make_program(year="2025/2026")
    program.requirements.append(Requirement(academic_year="2027/2028", applicant_category="international",
                                            status="verified_current", ielts_min=7))
    assert select_requirement(program, profile(intake_year=2027)).academic_year == "2027/2028"
    assert select_requirement(program, profile(intake_year=2026)).academic_year == "2025/2026"
    historical = evaluate(profile(intake_year=2026), program)
    assert historical.requirement_confidence == "historical"
    assert "historical:2025/2026" in historical.notes


def test_missing_language_and_hsk_remain_unknown():
    program = make_program(ielts=None)
    program.requirements[0].exams.append(ExamRequirement(
        exam_type="hsk", minimum_level="5", minimum_score=180,
        waiver_possible=True, status="verified_current"))
    missing = evaluate(profile(), program)
    assert missing.checks["hsk"] == "unknown"
    assert missing.checks["language"] == "unknown"
    assert "hsk_not_demonstrated" in missing.uncertainty
    met = evaluate(profile(hsk_level=5, hsk_score=190), program)
    assert met.checks["hsk"] == "met"
    assert met.checks["language"] == "met"


def test_finance_requires_same_currency_and_period():
    program = make_program()
    program.tuition_eur = 5000
    program.tuition_currency = "EUR"
    program.tuition_period = "semester"
    assert evaluate(profile(budget_eur=6000, budget_period="year"), program).checks["finance"] == "unknown"
    program.tuition_period = "year"
    assert evaluate(profile(budget_eur=6000, budget_period="year"), program).checks["finance"] == "met"
    assert evaluate(profile(budget_eur=3000, budget_period="year"), program).checks["finance"] == "not_met"
