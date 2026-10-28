from datetime import date, datetime, timezone
from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Country(Base):
    __tablename__ = "countries"
    iso_code: Mapped[str] = mapped_column(String(2), primary_key=True)
    name_en: Mapped[str] = mapped_column(String(100))
    name_az: Mapped[str] = mapped_column(String(100))
    name_ru: Mapped[str] = mapped_column(String(100))
    region: Mapped[str] = mapped_column(String(32))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class AcademicField(Base):
    __tablename__ = "academic_fields"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("academic_fields.id"), index=True)
    level: Mapped[str] = mapped_column(String(16), index=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    isced_code: Mapped[str | None] = mapped_column(String(4))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    parent: Mapped["AcademicField | None"] = relationship(remote_side="AcademicField.id")
    translations: Mapped[list["AcademicFieldTranslation"]] = relationship(back_populates="field")
    aliases: Mapped[list["AcademicFieldAlias"]] = relationship(back_populates="field")


class AcademicFieldTranslation(Base):
    __tablename__ = "academic_field_translations"
    __table_args__ = (UniqueConstraint("academic_field_id", "locale"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    academic_field_id: Mapped[int] = mapped_column(ForeignKey("academic_fields.id"), index=True)
    locale: Mapped[str] = mapped_column(String(2))
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    field: Mapped[AcademicField] = relationship(back_populates="translations")


class AcademicFieldAlias(Base):
    __tablename__ = "academic_field_aliases"
    __table_args__ = (UniqueConstraint("academic_field_id", "locale", "normalized_alias"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    academic_field_id: Mapped[int] = mapped_column(ForeignKey("academic_fields.id"), index=True)
    alias: Mapped[str] = mapped_column(String(200))
    locale: Mapped[str] = mapped_column(String(2))
    normalized_alias: Mapped[str] = mapped_column(String(200), index=True)
    field: Mapped[AcademicField] = relationship(back_populates="aliases")


class AcademicFieldRelation(Base):
    __tablename__ = "academic_field_relations"
    __table_args__ = (UniqueConstraint("source_field_id", "target_field_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    source_field_id: Mapped[int] = mapped_column(ForeignKey("academic_fields.id"), index=True)
    target_field_id: Mapped[int] = mapped_column(ForeignKey("academic_fields.id"), index=True)
    relationship_type: Mapped[str] = mapped_column(String(32))
    similarity_weight: Mapped[float] = mapped_column(Float)
    reason: Mapped[str | None] = mapped_column(Text)


class University(Base):
    __tablename__ = "universities"
    __table_args__ = (Index("ix_universities_name", "name"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    normalized_name: Mapped[str | None] = mapped_column(String(200), index=True)
    city: Mapped[str] = mapped_column(String(100))
    country: Mapped[str] = mapped_column(String(2), index=True)
    website: Mapped[str | None] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text)
    ror_id: Mapped[str | None] = mapped_column(String(64), unique=True, index=True)
    institution_type: Mapped[str | None] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32), default="active")
    source_url: Mapped[str | None] = mapped_column(String(500))
    retrieved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    programs: Mapped[list["Program"]] = relationship(back_populates="university")
    aliases: Mapped[list["UniversityAlias"]] = relationship(back_populates="university")
    identifiers: Mapped[list["UniversityIdentifier"]] = relationship(back_populates="university")


class UniversityAlias(Base):
    __tablename__ = "university_aliases"
    __table_args__ = (UniqueConstraint("university_id", "name"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    university_id: Mapped[int] = mapped_column(ForeignKey("universities.id"), index=True)
    name: Mapped[str] = mapped_column(String(250))
    locale: Mapped[str | None] = mapped_column(String(8))
    normalized_name: Mapped[str] = mapped_column(String(250), index=True)
    university: Mapped[University] = relationship(back_populates="aliases")


class UniversityIdentifier(Base):
    __tablename__ = "university_identifiers"
    __table_args__ = (UniqueConstraint("scheme", "value"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    university_id: Mapped[int] = mapped_column(ForeignKey("universities.id"), index=True)
    scheme: Mapped[str] = mapped_column(String(32))
    value: Mapped[str] = mapped_column(String(200))
    university: Mapped[University] = relationship(back_populates="identifiers")


class UniversitySource(Base):
    __tablename__ = "university_import_sources"
    __table_args__ = (UniqueConstraint("source", "source_record_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    university_id: Mapped[int] = mapped_column(ForeignKey("universities.id"), index=True)
    source: Mapped[str] = mapped_column(String(40))
    source_record_id: Mapped[str] = mapped_column(String(200))
    source_url: Mapped[str] = mapped_column(String(500))
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class UniversityReviewCandidate(Base):
    __tablename__ = "university_review_candidates"
    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(40))
    source_record_id: Mapped[str] = mapped_column(String(200), unique=True)
    candidate_university_id: Mapped[int | None] = mapped_column(ForeignKey("universities.id"))
    name: Mapped[str] = mapped_column(String(200))
    country: Mapped[str] = mapped_column(String(2))
    reason: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class ImportRun(Base):
    __tablename__ = "import_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(40))
    source_version: Mapped[str | None] = mapped_column(String(100))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), default="running")
    dry_run: Mapped[bool] = mapped_column(Boolean, default=False)
    processed: Mapped[int] = mapped_column(Integer, default=0)
    inserted: Mapped[int] = mapped_column(Integer, default=0)
    updated: Mapped[int] = mapped_column(Integer, default=0)
    skipped: Mapped[int] = mapped_column(Integer, default=0)
    errors: Mapped[int] = mapped_column(Integer, default=0)
    detail: Mapped[str | None] = mapped_column(Text)


class Program(Base):
    __tablename__ = "programs"
    __table_args__ = (Index("ix_programs_teaching_language", "teaching_language"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    university_id: Mapped[int] = mapped_column(ForeignKey("universities.id"))
    name: Mapped[str] = mapped_column(String(200))
    degree: Mapped[str] = mapped_column(String(16), index=True)
    field: Mapped[str] = mapped_column(String(64), index=True)
    academic_field_id: Mapped[int | None] = mapped_column(ForeignKey("academic_fields.id"), index=True)
    teaching_language: Mapped[str] = mapped_column(String(64), default="English")
    tuition_eur: Mapped[float | None] = mapped_column(Float)
    duration_months: Mapped[int | None] = mapped_column(Integer)
    credits_ects: Mapped[int | None] = mapped_column(Integer)
    description: Mapped[str | None] = mapped_column(Text)
    application_deadline: Mapped[date | None] = mapped_column(Date)
    official_url: Mapped[str | None] = mapped_column(String(500))
    source_publisher: Mapped[str | None] = mapped_column(String(200))
    retrieved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    verified_at: Mapped[date | None] = mapped_column(Date)
    data_status: Mapped[str] = mapped_column(String(32), default="partial")
    tuition_currency: Mapped[str | None] = mapped_column(String(3))
    tuition_period: Mapped[str | None] = mapped_column(String(20))
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    university: Mapped[University] = relationship(back_populates="programs")
    requirements: Mapped[list["Requirement"]] = relationship(back_populates="program", order_by="Requirement.academic_year.desc()")


class Requirement(Base):
    __tablename__ = "requirements"
    __table_args__ = (UniqueConstraint("program_id", "academic_year"),
                      Index("ix_requirements_year_status", "academic_year", "status"))
    id: Mapped[int] = mapped_column(primary_key=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("programs.id"))
    academic_year: Mapped[str] = mapped_column(String(9))
    applicant_category: Mapped[str] = mapped_column(String(64), default="all")
    min_gpa: Mapped[float | None] = mapped_column(Float)
    gpa_scale: Mapped[float | None] = mapped_column(Float)
    ielts_min: Mapped[float | None] = mapped_column(Float)
    toefl_min: Mapped[float | None] = mapped_column(Float)
    previous_field: Mapped[str | None] = mapped_column(String(64))
    previous_study_notes: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    source_url: Mapped[str | None] = mapped_column(String(500))
    source_publisher: Mapped[str | None] = mapped_column(String(200))
    retrieved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    verified_at: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(32), default="unverified")
    program: Mapped[Program] = relationship(back_populates="requirements")
    exams: Mapped[list["ExamRequirement"]] = relationship(back_populates="requirement")


class ExamRequirement(Base):
    __tablename__ = "exam_requirements"
    __table_args__ = (UniqueConstraint("requirement_id", "exam_type"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    requirement_id: Mapped[int] = mapped_column(ForeignKey("requirements.id"), index=True)
    exam_type: Mapped[str] = mapped_column(String(32))
    minimum_score: Mapped[float | None] = mapped_column(Float)
    score_scale: Mapped[str | None] = mapped_column(String(32))
    minimum_level: Mapped[str | None] = mapped_column(String(32))
    waiver_possible: Mapped[bool] = mapped_column(Boolean, default=False)
    source_url: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(32), default="unverified")
    requirement: Mapped[Requirement] = relationship(back_populates="exams")


class Scholarship(Base):
    __tablename__ = "scholarships"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    country: Mapped[str | None] = mapped_column(String(2))
    degree: Mapped[str | None] = mapped_column(String(16))
    coverage: Mapped[str] = mapped_column(String(64))
    description: Mapped[str] = mapped_column(Text)
    source_url: Mapped[str | None] = mapped_column(String(500))
    provider: Mapped[str | None] = mapped_column(String(200))
    academic_year: Mapped[str | None] = mapped_column(String(9))
    eligible_nationalities: Mapped[str | None] = mapped_column(Text)
    funding_components: Mapped[str | None] = mapped_column(Text)
    application_deadline: Mapped[date | None] = mapped_column(Date)
    verified_at: Mapped[date | None] = mapped_column(Date)
    verification_status: Mapped[str] = mapped_column(String(32), default="unverified")
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)


class SourceCheck(Base):
    __tablename__ = "source_checks"
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(500))
    checked_at: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(32))
    detail: Mapped[str | None] = mapped_column(Text)
