from datetime import date
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator


class RequirementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    academic_year: str
    min_gpa: float | None
    gpa_scale: float | None
    ielts_min: float | None
    toefl_min: float | None
    previous_field: str | None
    source_url: str | None
    verified_at: date | None
    status: str


class ProgramOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    degree: str
    field: str
    teaching_language: str
    tuition_eur: float | None
    duration_months: int | None
    official_url: str | None
    is_demo: bool
    requirements: list[RequirementOut] = []


class UniversityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    slug: str
    name: str
    city: str
    country: str
    website: str | None
    description: str | None
    is_demo: bool
    programs: list[ProgramOut] = []


class ScholarshipOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    country: str | None
    degree: str | None
    coverage: str
    description: str
    source_url: str | None
    is_demo: bool


class StudentProfile(BaseModel):
    degree: Literal["bachelor", "master", "phd"]
    academic_status: str | None = None
    field: str
    previous_field: str | None = None
    research_interests: str | None = None
    gpa: float | None = Field(default=None, ge=0, le=100)
    gpa_scale: float | None = Field(default=None, ge=1, le=100)
    ielts: float | None = Field(default=None, ge=0, le=9)
    toefl: float | None = Field(default=None, ge=0, le=120)
    sat: float | None = Field(default=None, ge=400, le=1600)
    gre: float | None = Field(default=None, ge=260, le=340)
    gmat: float | None = Field(default=None, ge=200, le=800)
    countries: list[str] = []
    university_id: int | None = None
    budget_eur: float | None = Field(default=None, ge=0)
    scholarship_priority: str = "preferred"
    teaching_language: str | None = None
    intake_year: int | None = Field(default=None, ge=2025, le=2100)
    semester: str | None = None
    citizenship: str = "AZ"
    study_format: str | None = None

    @model_validator(mode="after")
    def validate_grades(self):
        if self.gpa is not None and self.gpa_scale is not None and self.gpa > self.gpa_scale:
            raise ValueError("GPA cannot exceed its stated scale")
        return self


class MatchResult(BaseModel):
    program: ProgramOut
    university: UniversityOut
    score: int
    category: str
    uncertainty: list[str]
    notes: list[str]
    checks: dict[str, str]


class MatchResponse(BaseModel):
    results: list[MatchResult]
    total: int
    no_match_reason: str | None = None
    disclaimer: str = "Compatibility is a planning heuristic, not an admission probability or guarantee."
