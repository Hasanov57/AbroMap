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
    alembic("upgrade", "head")
    with sqlite3.connect(db_file) as db:
        assert db.execute("SELECT status FROM universities WHERE slug='demo-berlin-institute'").fetchone()[0] == "active"
        assert db.execute("SELECT COUNT(*) FROM academic_fields").fetchone()[0] == 0
        assert db.execute("SELECT version_num FROM alembic_version").fetchone()[0] == "bb2492674e67"
    backup = tmp_path / "before-cleanup.db"
    subprocess.run([sys.executable, "-m", "scripts.cleanup_demo", "--execute", "--confirm",
                    "DELETE_DEMO_RECORDS", "--backup-file", str(backup)],
                   cwd=backend, env=env, capture_output=True, text=True, check=True)
    with sqlite3.connect(backup) as db:
        assert db.execute("SELECT COUNT(*) FROM universities").fetchone()[0] == 2
    with sqlite3.connect(db_file) as db:
        assert db.execute("SELECT slug FROM universities").fetchall() == [("real-berlin-university",)]
