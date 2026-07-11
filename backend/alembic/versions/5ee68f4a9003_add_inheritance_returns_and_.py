"""Add inheritance returns and conversation_sessions

Revision ID: 5ee68f4a9003
Revises: 20260711_03_route_byte_offset
Create Date: 2026-07-11 13:02:12.447796

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5ee68f4a9003'
down_revision: Union[str, Sequence[str], None] = '20260711_03_route_byte_offset'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create rim_inheritance table
    op.create_table(
        'rim_inheritance',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('repository_id', sa.UUID(), nullable=False),
        sa.Column('repository_version_id', sa.UUID(), nullable=False),
        sa.Column('file_id', sa.UUID(), nullable=False),
        sa.Column('class_name', sa.String(), nullable=False),
        sa.Column('parent_name', sa.String(), nullable=False),
        sa.Column('inheritance_type', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['file_id'], ['rim_files.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rim_inheritance_repository_id'), 'rim_inheritance', ['repository_id'], unique=False)
    op.create_index(op.f('ix_rim_inheritance_repository_version_id'), 'rim_inheritance', ['repository_version_id'], unique=False)

    # 2. Create rim_returns table
    op.create_table(
        'rim_returns',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('repository_id', sa.UUID(), nullable=False),
        sa.Column('repository_version_id', sa.UUID(), nullable=False),
        sa.Column('file_id', sa.UUID(), nullable=False),
        sa.Column('function_name', sa.String(), nullable=False),
        sa.Column('return_type', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['file_id'], ['rim_files.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rim_returns_repository_id'), 'rim_returns', ['repository_id'], unique=False)
    op.create_index(op.f('ix_rim_returns_repository_version_id'), 'rim_returns', ['repository_version_id'], unique=False)

    # 3. Create conversation_sessions table
    op.create_table(
        'conversation_sessions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('repository_id', sa.UUID(), nullable=False),
        sa.Column('history', sa.JSON(), nullable=False),
        sa.Column('selected_graph_node', sa.String(length=255), nullable=True),
        sa.Column('active_filters', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['repository_id'], ['repositories.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversation_sessions_repository_id'), 'conversation_sessions', ['repository_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_conversation_sessions_repository_id'), table_name='conversation_sessions')
    op.drop_table('conversation_sessions')

    op.drop_index(op.f('ix_rim_returns_repository_version_id'), table_name='rim_returns')
    op.drop_index(op.f('ix_rim_returns_repository_id'), table_name='rim_returns')
    op.drop_table('rim_returns')

    op.drop_index(op.f('ix_rim_inheritance_repository_version_id'), table_name='rim_inheritance')
    op.drop_index(op.f('ix_rim_inheritance_repository_id'), table_name='rim_inheritance')
    op.drop_table('rim_inheritance')
