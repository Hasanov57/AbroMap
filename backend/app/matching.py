from .models import Program
from .schemas import MatchResult, ProgramOut, StudentProfile, UniversityOut

WEIGHTS = {"academic": 35, "language": 20, "financial": 25, "preference": 20}


def evaluate(profile: StudentProfile, program: Program) -> MatchResult | None:
    university = program.university
    if program.degree != profile.degree or program.field != profile.field:
        return None
    if profile.countries and university.country not in profile.countries:
        return None
    if profile.university_id and university.id != profile.university_id:
        return None

    requirement = program.requirements[0] if program.requirements else None
    checks: dict[str, str] = {}
    uncertainty: list[str] = []
    notes: list[str] = []
    component: dict[str, float] = {}
    historical = bool(requirement and (not profile.intake_year or requirement.academic_year != f"{profile.intake_year}/{profile.intake_year + 1}"))
    if historical:
        notes.append(f"historical:{requirement.academic_year}")
    if not requirement or requirement.status not in {"verified_current", "verified_historical"}:
        uncertainty.append("requirements_unverified")

    if requirement and requirement.previous_field:
        if not profile.previous_field:
            checks["previous_degree"] = "unknown"
            uncertainty.append("previous_field_missing")
        elif profile.previous_field != requirement.previous_field:
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
    component["academic"] = {"met": 1, "not_met": 0.15, "unknown": 0.5}[checks["gpa"]]

    if not requirement or (requirement.ielts_min is None and requirement.toefl_min is None):
        checks["language"] = "unknown"
        uncertainty.append("language_requirement_missing")
    elif profile.ielts is None and profile.toefl is None:
        checks["language"] = "unknown"
        uncertainty.append("language_score_missing")
    else:
        met = (profile.ielts is not None and requirement.ielts_min is not None and profile.ielts >= requirement.ielts_min) or (profile.toefl is not None and requirement.toefl_min is not None and profile.toefl >= requirement.toefl_min)
        comparable = (profile.ielts is not None and requirement.ielts_min is not None) or (profile.toefl is not None and requirement.toefl_min is not None)
        checks["language"] = "met" if met else "not_met" if comparable else "unknown"
    component["language"] = {"met": 1, "not_met": 0.1, "unknown": 0.5}[checks["language"]]

    if profile.scholarship_priority == "required":
        checks["finance"] = "unknown"
        uncertainty.append("scholarship_required_unverified")
    elif program.tuition_eur is None or profile.budget_eur is None:
        checks["finance"] = "unknown"
        uncertainty.append("finance_missing")
    elif program.tuition_eur <= profile.budget_eur:
        checks["finance"] = "met"
    else:
        checks["finance"] = "not_met"
        notes.append("tuition_above_budget")
    component["financial"] = {"met": 1, "not_met": 0.2, "unknown": 0.5}[checks["finance"]]
    preference = 1.0 if not profile.teaching_language or program.teaching_language.lower() == profile.teaching_language.lower() else 0.3
    component["preference"] = preference
    checks["preference"] = "met" if preference == 1 else "not_met"

    score = round(sum(component[key] * weight for key, weight in WEIGHTS.items()))
    if not requirement or requirement.status not in {"verified_current", "verified_historical"}:
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
                       score=score, category=category, uncertainty=uncertainty, notes=notes, checks=checks)
