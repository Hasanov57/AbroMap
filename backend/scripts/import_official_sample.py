"""Idempotently load four source-checked degree programs and one scholarship."""

import argparse
from datetime import date, datetime, timezone

from sqlalchemy import select

from app.catalog import load_data
from app.db import SessionLocal
from app.models import AcademicField, ExamRequirement, Program, Requirement, Scholarship, University


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", help="Write records; default is dry run")
    args = parser.parse_args()
    data = load_data("official_sample.json")
    checked = date.fromisoformat(data["checked_on"])
    checked_at = datetime.combine(checked, datetime.min.time(), tzinfo=timezone.utc)
    with SessionLocal() as db:
        for item in data["programs"]:
            university = db.scalar(select(University).where(University.ror_id == item["ror_id"],
                                                             University.is_demo.is_(False)))
            if university is None:
                parser.error(f"Import the ROR institution first: {item['ror_id']}")
            field = db.scalar(select(AcademicField).where(AcademicField.slug == item["field"]))
            if field is None:
                parser.error("Run python -m scripts.import_fields first")
            program = db.scalar(select(Program).where(Program.university_id == university.id,
                                                       Program.official_url == item["official_url"]))
            print(f"{'update' if program else 'insert'} {university.name}: {item['name']}")
            if not args.execute:
                continue
            if program is None:
                program = Program(university_id=university.id, official_url=item["official_url"])
                db.add(program)
            for key in ("name", "degree", "teaching_language", "duration_months", "credits_ects",
                        "description", "source_publisher"):
                setattr(program, key, item.get(key))
            program.field = item["field"]
            program.academic_field_id = field.id
            program.application_deadline = date.fromisoformat(item["application_deadline"]) if item.get("application_deadline") else None
            program.retrieved_at = checked_at
            program.verified_at = checked
            program.data_status = "verified_source"
            program.is_demo = False
            db.flush()
            evidence = item["requirement"]
            for previous in db.scalars(select(Requirement).where(Requirement.program_id == program.id,
                                                                 Requirement.source_url == evidence["source_url"],
                                                                 Requirement.academic_year != evidence["academic_year"])):
                if previous.status == "verified_current":
                    previous.status = "superseded"
            requirement = db.scalar(select(Requirement).where(Requirement.program_id == program.id,
                                                                Requirement.academic_year == evidence["academic_year"]))
            if requirement is None:
                requirement = Requirement(program_id=program.id, academic_year=evidence["academic_year"])
                db.add(requirement)
            for key in ("status", "applicant_category", "previous_study_notes", "notes", "source_url", "source_publisher"):
                setattr(requirement, key, evidence.get(key))
            requirement.retrieved_at = checked_at
            requirement.verified_at = checked
            db.flush()
            for exam in evidence.get("exams", []):
                row = db.scalar(select(ExamRequirement).where(ExamRequirement.requirement_id == requirement.id,
                                                                ExamRequirement.exam_type == exam["exam_type"]))
                if row is None:
                    row = ExamRequirement(requirement_id=requirement.id, exam_type=exam["exam_type"])
                    db.add(row)
                for key in ("minimum_score", "minimum_level", "status", "waiver_possible"):
                    setattr(row, key, exam.get(key))
                row.source_url = evidence["source_url"]
        for item in data["scholarships"]:
            row = db.scalar(select(Scholarship).where(Scholarship.name == item["name"]))
            print(f"{'update' if row else 'insert'} scholarship: {item['name']}")
            if not args.execute:
                continue
            if row is None:
                row = Scholarship(name=item["name"])
                db.add(row)
            for key in ("provider", "country", "degree", "coverage", "description", "source_url",
                        "eligible_nationalities", "funding_components", "verification_status"):
                setattr(row, key, item.get(key))
            row.verified_at = checked
            row.is_demo = False
        if args.execute:
            db.commit()


if __name__ == "__main__":
    main()
