"""Allow a source to leave the admission year unstated.

Revision ID: c1a4c01bde9e
Revises: bb2492674e67
"""

from alembic import op
import sqlalchemy as sa


revision = "c1a4c01bde9e"
down_revision = "bb2492674e67"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("requirements") as batch:
        batch.alter_column("academic_year", existing_type=sa.String(9),
                           type_=sa.String(32), existing_nullable=False)


def downgrade() -> None:
    with op.batch_alter_table("requirements") as batch:
        batch.alter_column("academic_year", existing_type=sa.String(32),
                           type_=sa.String(9), existing_nullable=False)
