from app.config import Settings


def test_supabase_uri_selects_installed_psycopg_driver():
    settings = Settings(database_url="postgresql://user:secret@pooler.example:5432/postgres?sslmode=require")
    assert settings.database_url == "postgresql+psycopg://user:secret@pooler.example:5432/postgres?sslmode=require"


def test_local_sqlite_url_is_unchanged():
    settings = Settings(database_url="sqlite:///./test.db")
    assert settings.database_url == "sqlite:///./test.db"
