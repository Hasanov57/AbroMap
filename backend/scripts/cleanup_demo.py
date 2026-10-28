"""Safely remove only the five known AbroMap sample institutions and scholarship."""

import argparse
import sqlite3
from datetime import datetime
from pathlib import Path

from sqlalchemy import delete, select

from app.db import SessionLocal, engine
from app.models import ExamRequirement, Program, Requirement, Scholarship, University


DEMO_SLUGS = {
    "demo-berlin-institute", "demo-milan-academy", "demo-budapest-college",
    "demo-hamburg-school", "demo-rome-institute",
}
DEMO_SCHOLARSHIP = "Demo full scholarship"


def selected_ids(db):
    universities = db.scalars(select(University).where(University.slug.in_(DEMO_SLUGS),
                                                       University.is_demo.is_(True))).all()
    university_ids = [item.id for item in universities]
    program_ids = db.scalars(select(Program.id).where(Program.university_id.in_(university_ids),
                                                      Program.is_demo.is_(True))).all() if university_ids else []
    scholarship_ids = db.scalars(select(Scholarship.id).where(Scholarship.name == DEMO_SCHOLARSHIP,
                                                               Scholarship.is_demo.is_(True))).all()
    return university_ids, program_ids, scholarship_ids


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", help="Apply deletion after a backup")
    parser.add_argument("--confirm", help="Required exact value: DELETE_DEMO_RECORDS")
    parser.add_argument("--backup-file", type=Path,
                        help="Existing pg_dump backup for PostgreSQL; SQLite creates this file automatically")
    args = parser.parse_args()
    with SessionLocal() as db:
        university_ids, program_ids, scholarship_ids = selected_ids(db)
        print({"universities": len(university_ids), "programs": len(program_ids),
               "scholarships": len(scholarship_ids), "university_ids": university_ids})
        if not args.execute:
            print("Dry run only. Use --execute --confirm DELETE_DEMO_RECORDS after reviewing the selection.")
            return
        if args.confirm != "DELETE_DEMO_RECORDS":
            parser.error("Execution requires --confirm DELETE_DEMO_RECORDS")
        if engine.url.get_backend_name() == "sqlite":
            db_path = engine.url.database
            if not db_path or db_path == ":memory:":
                parser.error("Cannot back up an in-memory SQLite database")
            backup = args.backup_file or Path(db_path).with_name(
                f"abromap-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}.db")
            if backup.exists():
                parser.error(f"Backup already exists: {backup}")
            db.rollback()
            with sqlite3.connect(db_path) as source, sqlite3.connect(backup) as target:
                source.backup(target)
            print(f"Database backup created: {backup.resolve()}")
        elif not args.backup_file or not args.backup_file.is_file() or args.backup_file.stat().st_size == 0:
            parser.error("PostgreSQL execution requires --backup-file pointing to a completed pg_dump")
        try:
            requirement_ids = db.scalars(select(Requirement.id).where(
                Requirement.program_id.in_(program_ids))).all() if program_ids else []
            if requirement_ids:
                db.execute(delete(ExamRequirement).where(ExamRequirement.requirement_id.in_(requirement_ids)))
                db.execute(delete(Requirement).where(Requirement.id.in_(requirement_ids)))
            if program_ids:
                db.execute(delete(Program).where(Program.id.in_(program_ids)))
            if university_ids:
                db.execute(delete(University).where(University.id.in_(university_ids)))
            if scholarship_ids:
                db.execute(delete(Scholarship).where(Scholarship.id.in_(scholarship_ids)))
            db.commit()
        except Exception:
            db.rollback()
            raise
        print("Known demonstration records removed. Re-running is safe.")


if __name__ == "__main__":
    main()
