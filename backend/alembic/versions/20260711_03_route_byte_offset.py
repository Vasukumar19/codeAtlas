"""Add byte offsets to rim routes.

Revision ID: 20260711_03_route_byte_offset
Revises: 20260711_02_call_metadata
Create Date: 2026-07-11
"""

import sqlalchemy as sa
from alembic import op

revision = "20260711_03_route_byte_offset"
down_revision = "20260711_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("rim_routes", sa.Column("byte_offset", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("rim_routes", "byte_offset")
