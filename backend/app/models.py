from datetime import date
from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base


class University(Base):
    __tablename__ = "universities"
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    city: Mapped[str] = mapped_column(String(100))
    country: Mapped[str] = mapped_column(String(2), index=True)
    website: Mapped[str | None] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=True)
    programs: Mapped[list["Program"]] = relationship(back_populates="university")


class Program(Base):
    __tablename__ = "programs"
    id: Mapped[int] = mapped_column(primary_key=True)
    university_id: Mapped[int] = mapped_column(ForeignKey("universities.id"))
    name: Mapped[str] = mapped_column(String(200))
    degree: Mapped[str] = mapped_column(String(16), index=True)
    field: Mapped[str] = mapped_column(String(64), index=True)
    teaching_language: Mapped[str] = mapped_column(String(64), default="English")
    tuition_eur: Mapped[float | None] = mapped_column(Float)
    duration_months: Mapped[int | None] = mapped_column(Integer)
    official_url: Mapped[str | None] = mapped_column(String(500))
    is_demo: Mapped[bool] = mapped_column(Boolean, default=True)
    university: Mapped[University] = relationship(back_populates="programs")
    requirements: Mapped[list["Requirement"]] = relationship(back_populates="program", order_by="Requirement.academic_year.desc()")


class Requirement(Base):
    __tablename__ = "requirements"
    __table_args__ = (UniqueConstraint("program_id", "academic_year"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("programs.id"))
    academic_year: Mapped[str] = mapped_column(String(9))
    min_gpa: Mapped[float | None] = mapped_column(Float)
    gpa_scale: Mapped[float | None] = mapped_column(Float)
    ielts_min: Mapped[float | None] = mapped_column(Float)
    toefl_min: Mapped[float | None] = mapped_column(Float)
    previous_field: Mapped[str | None] = mapped_column(String(64))
    source_url: Mapped[str | None] = mapped_column(String(500))
    verified_at: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(32), default="unverified")
    program: Mapped[Program] = relationship(back_populates="requirements")


class Scholarship(Base):
    __tablename__ = "scholarships"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    country: Mapped[str | None] = mapped_column(String(2))
    degree: Mapped[str | None] = mapped_column(String(16))
    coverage: Mapped[str] = mapped_column(String(64))
    description: Mapped[str] = mapped_column(Text)
    source_url: Mapped[str | None] = mapped_column(String(500))
    is_demo: Mapped[bool] = mapped_column(Boolean, default=True)


class SourceCheck(Base):
    __tablename__ = "source_checks"
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(500))
    checked_at: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(32))
    detail: Mapped[str | None] = mapped_column(Text)
