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
    previous_study_notes: str | None = None
    notes: str | None = None
    source_url: str | None
    source_publisher: str | None = None
    verified_at: date | None
    status: str
    exams: list["ExamRequirementOut"] = []


class ExamRequirementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    exam_type: str
    minimum_score: float | None
    score_scale: str | None
    minimum_level: str | None
    waiver_possible: bool
    source_url: str | None
    status: str


class UniversityBriefOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    slug: str
    name: str
    city: str
    country: str


class ProgramOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    degree: str
    field: str
    teaching_language: str
    tuition_eur: float | None
    duration_months: int | None
    credits_ects: int | None = None
    description: str | None = None
    application_deadline: date | None = None
    official_url: str | None
    source_publisher: str | None = None
    verified_at: date | None = None
    data_status: str = "partial"
    tuition_currency: str | None = None
    tuition_period: str | None = None
    is_demo: bool
    requirements: list[RequirementOut] = []
    university: UniversityBriefOut | None = None


class UniversityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    slug: str
    name: str
    city: str
    country: str
    website: str | None
    description: str | None
    ror_id: str | None = None
    institution_type: str | None = None
    source_url: str | None = None
    aliases: list["UniversityAliasOut"] = []
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
    provider: str | None = None
    academic_year: str | None = None
    eligible_nationalities: str | None = None
    funding_components: str | None = None
    application_deadline: date | None = None
    verified_at: date | None = None
    verification_status: str = "unverified"
    is_demo: bool


class UniversityAliasOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    locale: str | None


class CountryOut(BaseModel):
    iso_code: str
    name: str
    region: str
    university_count: int
    program_count: int
    verified_program_count: int


class AcademicFieldOut(BaseModel):
    id: int
    slug: str
    name: str
    category: str
    isced_code: str | None


class UniversitySearchOut(BaseModel):
    id: int
    slug: str
    name: str
    city: str
    country: str
    website: str | None
    ror_id: str | None
    program_count: int


class UniversityPage(BaseModel):
    items: list[UniversitySearchOut]
    total: int
    page: int
    page_size: int
    total_pages: int


class StudentProfile(BaseModel):
    degree: Literal["bachelor", "master", "phd"]
    academic_status: str | None = None
    field: str
    custom_field: str | None = None
    previous_field: str | None = None
    research_interests: str | None = None
    gpa: float | None = Field(default=None, ge=0, le=100)
    gpa_scale: float | None = Field(default=None, ge=1, le=100)
    ielts: float | None = Field(default=None, ge=0, le=9)
    toefl: float | None = Field(default=None, ge=0, le=120)
    hsk_level: int | None = Field(default=None, ge=1, le=9)
    hsk_score: float | None = Field(default=None, ge=0, le=300)
    english_cefr: str | None = None
    sat: float | None = Field(default=None, ge=400, le=1600)
    gre: float | None = Field(default=None, ge=260, le=340)
    gmat: float | None = Field(default=None, ge=200, le=800)
    countries: list[str] = []
    university_id: int | None = None
    budget_eur: float | None = Field(default=None, ge=0)
    budget_period: str | None = None
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
    subject_match: str = "exact"
    requirement_confidence: str = "unknown"


class MatchResponse(BaseModel):
    results: list[MatchResult]
    total: int
    page: int = 1
    page_size: int = 20
    no_match_reason: str | None = None
    disclaimer: str = "Compatibility is a planning heuristic, not an admission probability or guarantee."
