"""Protect application tables exposed by Supabase's public Data API.

Revision ID: e6a51a9c3b24
Revises: c1a4c01bde9e
"""

from alembic import op


revision = "e6a51a9c3b24"
down_revision = "c1a4c01bde9e"
branch_labels = None
depends_on = None


TABLES = (
    "academic_field_aliases",
    "academic_field_relations",
    "academic_field_translations",
    "academic_fields",
    "alembic_version",
    "countries",
    "exam_requirements",
    "import_runs",
    "programs",
    "requirements",
    "scholarships",
    "source_checks",
    "universities",
    "university_aliases",
    "university_identifiers",
    "university_import_sources",
    "university_review_candidates",
)


def upgrade() -> None:
    if op.get_bind().dialect.name == "postgresql":
        for table in TABLES:
            op.execute(f'ALTER TABLE public."{table}" ENABLE ROW LEVEL SECURITY')


def downgrade() -> None:
    if op.get_bind().dialect.name == "postgresql":
        for table in TABLES:
            op.execute(f'ALTER TABLE public."{table}" DISABLE ROW LEVEL SECURITY')
