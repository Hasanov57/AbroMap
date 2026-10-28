from app.matching import evaluate
from app.models import Program, Requirement, University
from app.schemas import StudentProfile


def make_program(ielts=6.5, gpa=3.0, scale=4.0):
    university = University(id=1, slug="demo", name="Demo", city="Berlin", country="DE", is_demo=True)
    program = Program(id=1, name="MSc Computer Science", degree="master", field="computer_science",
                      university=university, teaching_language="English", tuition_eur=3000, is_demo=True)
    program.requirements = [Requirement(academic_year="2025/2026", ielts_min=ielts, min_gpa=gpa, gpa_scale=scale, status="unverified")]
    university.programs = [program]
    return program


def profile(**kwargs):
    return StudentProfile(degree="master", field="computer_science", **kwargs)


def test_language_met():
    assert evaluate(profile(ielts=7), make_program()).checks["language"] == "met"


def test_language_not_met():
    assert evaluate(profile(ielts=6), make_program(ielts=7)).checks["language"] == "not_met"


def test_missing_is_unknown():
    assert evaluate(profile(), make_program(ielts=None)).checks["language"] == "unknown"


def test_no_gpa_conversion():
    result = evaluate(profile(gpa=85, gpa_scale=100), make_program())
    assert result.checks["gpa"] == "unknown"


def test_historical_labeled():
    result = evaluate(profile(intake_year=2027), make_program())
    assert any("historical" in note for note in result.notes)


def test_filters():
    assert evaluate(profile(countries=["IT"]), make_program()) is None
    assert evaluate(StudentProfile(degree="bachelor", field="computer_science"), make_program()) is None


def test_score_is_deterministic():
    first = evaluate(profile(ielts=7, gpa=3.5, gpa_scale=4, budget_eur=5000), make_program())
    second = evaluate(profile(ielts=7, gpa=3.5, gpa_scale=4, budget_eur=5000), make_program())
    assert first.score == second.score == 69


def test_full_scholarship_is_not_assumed_from_zero_tuition():
    result = evaluate(profile(budget_eur=0, scholarship_priority="required"), make_program())
    assert result.checks["finance"] == "unknown"
    assert "scholarship_required_unverified" in result.uncertainty
