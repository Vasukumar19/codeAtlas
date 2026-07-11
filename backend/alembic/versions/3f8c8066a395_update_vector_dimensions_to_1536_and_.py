"""Update vector dimensions to 1536 and add rim_calls

Revision ID: 3f8c8066a395
Revises: 20260710_01
Create Date: 2026-07-11 00:59:48.553756

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3f8c8066a395'
down_revision: Union[str, Sequence[str], None] = '20260710_01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Update vector dimensions
    op.execute('ALTER TABLE rim_files ALTER COLUMN embedding TYPE vector(1536);')
    op.execute('ALTER TABLE rim_symbols ALTER COLUMN embedding TYPE vector(1536);')
    op.execute('ALTER TABLE embedding_metadata ALTER COLUMN vector TYPE vector(1536);')

    # Create rim_calls table
    op.create_table(
        'rim_calls',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('repository_id', sa.UUID(), nullable=False),
        sa.Column('repository_version_id', sa.UUID(), nullable=False),
        sa.Column('file_id', sa.UUID(), nullable=False),
        sa.Column('function_name', sa.String(), nullable=False),
        sa.Column('receiver', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['file_id'], ['rim_files.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rim_calls_repository_id'), 'rim_calls', ['repository_id'], unique=False)
    op.create_index(op.f('ix_rim_calls_repository_version_id'), 'rim_calls', ['repository_version_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_rim_calls_repository_version_id'), table_name='rim_calls')
    op.drop_index(op.f('ix_rim_calls_repository_id'), table_name='rim_calls')
    op.drop_table('rim_calls')

    op.execute('ALTER TABLE embedding_metadata ALTER COLUMN vector TYPE vector(768);')
    op.execute('ALTER TABLE rim_symbols ALTER COLUMN embedding TYPE vector(768);')
    op.execute('ALTER TABLE rim_files ALTER COLUMN embedding TYPE vector(768);')
