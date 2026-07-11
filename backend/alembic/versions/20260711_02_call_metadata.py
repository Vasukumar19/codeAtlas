"""Add caller metadata to RIM calls.

Revision ID: 20260711_02
Revises: 3f8c8066a395
Create Date: 2026-07-11
"""

import sqlalchemy as sa
from alembic import op

revision = "20260711_02"
down_revision = "3f8c8066a395"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("rim_calls", sa.Column("caller_function_name", sa.String(), nullable=True))
    op.add_column("rim_calls", sa.Column("byte_offset", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("rim_calls", "byte_offset")
    op.drop_column("rim_calls", "caller_function_name")
