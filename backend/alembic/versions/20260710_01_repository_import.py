"""Create repository import tables.

Revision ID: 20260710_01
Revises:
Create Date: 2026-07-10
"""

import sqlalchemy as sa
from alembic import op

revision = "20260710_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the persistence model required by the repository import service."""
    repository_state = sa.Enum("NEW", "QUEUED", "CLONING", "READY_TO_PARSE", "FAILED", name="repositorystate")
    job_state = sa.Enum("QUEUED", "RUNNING", "SUCCEEDED", "FAILED", name="jobstate")
    repository_state.create(op.get_bind(), checkfirst=True)
    job_state.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "repositories",
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("owner", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("remote_url", sa.String(length=2048), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("default_branch", sa.String(length=255), nullable=False),
        sa.Column("current_branch", sa.String(length=255), nullable=False),
        sa.Column("latest_commit", sa.String(length=64), nullable=True),
        sa.Column("primary_language", sa.String(length=255), nullable=True),
        sa.Column("topics", sa.JSON(), nullable=False),
        sa.Column("stars", sa.Integer(), nullable=False),
        sa.Column("forks", sa.Integer(), nullable=False),
        sa.Column("state", repository_state, nullable=False),
        sa.Column("clone_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.Column("snapshot_path", sa.String(length=2048), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider", "owner", "name"),
    )
    op.create_table(
        "repository_versions",
        sa.Column("repository_id", sa.Uuid(), nullable=False),
        sa.Column("commit_hash", sa.String(length=64), nullable=False),
        sa.Column("branch_name", sa.String(length=255), nullable=False),
        sa.Column("snapshot_path", sa.String(length=2048), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("repository_id", "commit_hash"),
    )
    op.create_table(
        "import_jobs",
        sa.Column("repository_id", sa.Uuid(), nullable=False),
        sa.Column("repository_version_id", sa.Uuid(), nullable=True),
        sa.Column("state", job_state, nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["repository_id"], ["repositories.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["repository_version_id"], ["repository_versions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Remove the repository import persistence model."""
    op.drop_table("import_jobs")
    op.drop_table("repository_versions")
    op.drop_table("repositories")
    sa.Enum(name="jobstate").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="repositorystate").drop(op.get_bind(), checkfirst=True)
