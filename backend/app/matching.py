"""Explainable compatibility screening. Scores are not admission probabilities."""

from datetime import date

from .models import Program, Requirement
from .schemas import MatchResult, ProgramOut, StudentProfile, UniversityOut


WEIGHTS = {"academic": 35, "language": 20, "financial": 25, "preference": 20}
VERIFIED = {"verified_current", "verified_historical"}
CEFR = {"A1": 1, "A2": 2, "B1": 3, "B2": 4, "C1": 5, "C2": 6}


def select_requirement(program: Program, profile: StudentProfile) -> Requirement | None:
    """Prefer the requested intake and applicable applicant category."""
    rows = [row for row in program.requirements
            if row.applicant_category in {"all", "international"}]
    if not rows:
        return None
    target = profile.intake_year
    if target is None:
        return max(rows, key=lambda row: (row.status in VERIFIED, row.academic_year))
    exact = [row for row in rows if row.academic_year == f"{target}/{target + 1}"]
    if exact:
        return max(exact, key=lambda row: row.status in VERIFIED)
    previous = [row for row in rows if row.academic_year[:4].isdigit()
                and int(row.academic_year[:4]) < target]
    verified_previous = [row for row in previous if row.status in VERIFIED]
    if verified_previous:
        return max(verified_previous, key=lambda row: row.academic_year)
    return next((row for row in rows if row.academic_year == "not stated"), None) or (
        max(previous, key=lambda row: row.academic_year) if previous else None)


def _exam_check(profile: StudentProfile, requirement: Requirement, checks: dict[str, str],
                uncertainty: list[str], notes: list[str]) -> list[str]:
    outcomes = []
    for exam in requirement.exams:
        result = "unknown"
        if exam.exam_type == "hsk":
            if profile.hsk_level is not None:
                level_met = exam.minimum_level is None or profile.hsk_level >= int(exam.minimum_level)
                score_met = exam.minimum_score is None or (
                    profile.hsk_score is not None and profile.hsk_score >= exam.minimum_score)
                result = "met" if level_met and score_met else "unknown" if exam.waiver_possible else "not_met"
        elif exam.exam_type == "english_cefr":
            if profile.english_cefr and exam.minimum_level:
                result = "met" if CEFR.get(profile.english_cefr.upper(), 0) >= CEFR.get(exam.minimum_level, 99) else "not_met"
        checks[exam.exam_type] = result
        outcomes.append(result)
        if result == "unknown":
            uncertainty.append(f"{exam.exam_type}_not_demonstrated")
        if exam.waiver_possible:
            notes.append(f"{exam.exam_type}_waiver_may_apply")
    return outcomes


def evaluate(profile: StudentProfile, program: Program, *, subject_match: str = "exact",
             similarity: float = 1.0) -> MatchResult | None:
    university = program.university
    if program.degree != profile.degree:
        return None
    if subject_match == "exact" and program.field.replace("_", "-") != profile.field.replace("_", "-"):
        return None
    if profile.countries and university.country not in profile.countries:
        return None
    if profile.university_id and university.id != profile.university_id:
        return None

    requirement = select_requirement(program, profile)
    checks: dict[str, str] = {"subject": subject_match}
    uncertainty: list[str] = []
    notes: list[str] = []
    component: dict[str, float] = {}
    historical = bool(requirement and profile.intake_year and requirement.academic_year[:4].isdigit() and
                      requirement.academic_year != f"{profile.intake_year}/{profile.intake_year + 1}")
    if requirement and not profile.intake_year and requirement.status == "verified_historical":
        historical = True
    if historical:
        notes.append(f"historical:{requirement.academic_year}")
    if not requirement or requirement.status not in VERIFIED:
        uncertainty.append("requirements_unverified")
    if subject_match != "exact":
        notes.append("related_subject_not_admission_eligibility")
        uncertainty.append("subject_prerequisites_unverified")

    if requirement and requirement.previous_study_notes:
        checks["previous_degree"] = "unknown"
        uncertainty.append("program_specific_prerequisites")
    elif requirement and requirement.previous_field:
        if not profile.previous_field:
            checks["previous_degree"] = "unknown"
            uncertainty.append("previous_field_missing")
        elif profile.previous_field.replace("_", "-") != requirement.previous_field.replace("_", "-"):
            checks["previous_degree"] = "not_met"
        else:
            checks["previous_degree"] = "met"

    if not requirement or requirement.min_gpa is None or requirement.gpa_scale is None:
        checks["gpa"] = "unknown"
        uncertainty.append("gpa_requirement_missing")
    elif profile.gpa is None or profile.gpa_scale is None:
        checks["gpa"] = "unknown"
        uncertainty.append("student_gpa_missing")
    elif profile.gpa_scale != requirement.gpa_scale:
        checks["gpa"] = "unknown"
        uncertainty.append("gpa_scale_mismatch")
    else:
        checks["gpa"] = "met" if profile.gpa >= requirement.min_gpa else "not_met"
    component["academic"] = {"met": 1, "not_met": .15, "unknown": .5}[checks["gpa"]] * similarity

    if not requirement or (requirement.ielts_min is None and requirement.toefl_min is None):
        legacy_language = "unknown"
    elif profile.ielts is None and profile.toefl is None:
        legacy_language = "unknown"
    else:
        met = ((profile.ielts is not None and requirement.ielts_min is not None and
                profile.ielts >= requirement.ielts_min) or
               (profile.toefl is not None and requirement.toefl_min is not None and
                profile.toefl >= requirement.toefl_min))
        comparable = ((profile.ielts is not None and requirement.ielts_min is not None) or
                      (profile.toefl is not None and requirement.toefl_min is not None))
        legacy_language = "met" if met else "not_met" if comparable else "unknown"
    exam_outcomes = _exam_check(profile, requirement, checks, uncertainty, notes) if requirement else []
    if requirement and (requirement.ielts_min is not None or requirement.toefl_min is not None):
        language_outcomes = [legacy_language] + exam_outcomes
    else:
        language_outcomes = exam_outcomes
    if not language_outcomes:
        checks["language"] = "unknown"
        uncertainty.append("language_requirement_missing")
    elif "not_met" in language_outcomes:
        checks["language"] = "not_met"
    elif "unknown" in language_outcomes:
        checks["language"] = "unknown"
    else:
        checks["language"] = "met"
    component["language"] = {"met": 1, "not_met": .1, "unknown": .5}[checks["language"]]

    if profile.scholarship_priority == "required":
        checks["finance"] = "unknown"
        uncertainty.append("scholarship_required_unverified")
    elif (program.tuition_eur is None or profile.budget_eur is None or
          program.tuition_currency != "EUR" or program.tuition_period != "year" or
          profile.budget_period != "year"):
        checks["finance"] = "unknown"
        uncertainty.append("finance_not_comparable")
    elif program.tuition_eur <= profile.budget_eur:
        checks["finance"] = "met"
    else:
        checks["finance"] = "not_met"
        notes.append("tuition_above_budget")
    component["financial"] = {"met": 1, "not_met": .2, "unknown": .5}[checks["finance"]]
    preference = 1.0 if not profile.teaching_language or program.teaching_language.lower() == profile.teaching_language.lower() else .3
    component["preference"] = preference
    checks["preference"] = "met" if preference == 1 else "not_met"

    score = round(sum(component[key] * weight for key, weight in WEIGHTS.items()))
    confidence = "missing" if not requirement else "unverified" if requirement.status not in VERIFIED else "historical" if historical else "verified"
    if confidence in {"missing", "unverified"}:
        score = min(score, 69)
    elif historical:
        score = min(score, 79)
    if any(checks.get(key) == "not_met" for key in ("gpa", "language", "previous_degree")):
        category = "requirements_not_met"
    elif len(uncertainty) >= 3:
        category = "insufficient_information"
    elif score >= 80:
        category = "strong_match"
    elif score >= 65:
        category = "good_match"
    else:
        category = "possible_match"
    return MatchResult(program=ProgramOut.model_validate(program), university=UniversityOut.model_validate(university),
                       score=score, category=category, uncertainty=uncertainty, notes=notes, checks=checks,
                       subject_match=subject_match, requirement_confidence=confidence)
