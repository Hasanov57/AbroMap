import os
import sqlite3
import subprocess
import sys
from pathlib import Path


def test_existing_sqlite_database_upgrades(tmp_path):
    backend = Path(__file__).resolve().parents[1]
    db_file = tmp_path / "upgrade.db"
    env = {**os.environ, "DATABASE_URL": f"sqlite:///{db_file.as_posix()}"}
    def alembic(*args):
        subprocess.run([sys.executable, "-m", "alembic", *args], cwd=backend,
                       env=env, capture_output=True, text=True, check=True)
    alembic("upgrade", "555d73c045ac")
    with sqlite3.connect(db_file) as db:
        db.execute("INSERT INTO universities (slug,name,city,country,is_demo) VALUES (?,?,?,?,?)",
                   ("demo-berlin-institute", "Demo Berlin Institute", "Berlin", "DE", 1))
        db.execute("INSERT INTO universities (slug,name,city,country,is_demo) VALUES (?,?,?,?,?)",
                   ("real-berlin-university", "Real Berlin University", "Berlin", "DE", 0))
        real_id = db.execute("SELECT id FROM universities WHERE slug='real-berlin-university'").fetchone()[0]
        db.execute("INSERT INTO programs (university_id,name,degree,field,teaching_language,is_demo) VALUES (?,?,?,?,?,?)",
                   (real_id, "Real program", "master", "computer-science", "English", 0))
        program_id = db.execute("SELECT id FROM programs WHERE university_id=?", (real_id,)).fetchone()[0]
        db.execute("INSERT INTO requirements (program_id,academic_year,status) VALUES (?,?,?)",
                   (program_id, "2026/2027", "verified_current"))
    alembic("upgrade", "bb2492674e67")
    with sqlite3.connect(db_file) as db:
        old_type = next(row[2] for row in db.execute("PRAGMA table_info(requirements)") if row[1] == "academic_year")
        assert old_type == "VARCHAR(9)"
    alembic("upgrade", "head")
    with sqlite3.connect(db_file) as db:
        assert db.execute("SELECT status FROM universities WHERE slug='demo-berlin-institute'").fetchone()[0] == "active"
        assert db.execute("SELECT COUNT(*) FROM academic_fields").fetchone()[0] == 0
        assert db.execute("SELECT version_num FROM alembic_version").fetchone()[0] == "c1a4c01bde9e"
        new_type = next(row[2] for row in db.execute("PRAGMA table_info(requirements)") if row[1] == "academic_year")
        assert new_type == "VARCHAR(32)"
        assert db.execute("SELECT academic_year FROM requirements").fetchall() == [("2026/2027",)]
    backup = tmp_path / "before-cleanup.db"
    subprocess.run([sys.executable, "-m", "scripts.cleanup_demo", "--execute", "--confirm",
                    "DELETE_DEMO_RECORDS", "--backup-file", str(backup)],
                   cwd=backend, env=env, capture_output=True, text=True, check=True)
    with sqlite3.connect(backup) as db:
        assert db.execute("SELECT COUNT(*) FROM universities").fetchone()[0] == 2
    with sqlite3.connect(db_file) as db:
        assert db.execute("SELECT slug FROM universities").fetchall() == [("real-berlin-university",)]
        assert db.execute("SELECT academic_year FROM requirements").fetchall() == [("2026/2027",)]
