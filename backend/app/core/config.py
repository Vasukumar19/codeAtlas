"""Application settings loaded from environment variables."""

from pathlib import Path

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed runtime configuration with local development defaults."""

    project_name: str = "CodeAtlas"
    version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"
    postgres_server: str = "localhost"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "codeatlas"
    postgres_port: int = 5432
    database_url: str | None = None
    repository_storage_path: Path = Path(".data/repositories")
    github_api_url: str = "https://api.github.com"
    github_token: str | None = None
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[3] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @computed_field
    @property
    def sqlalchemy_database_uri(self) -> str:
        """Return the configured async SQLAlchemy connection URL."""
        return self.database_url or (
            "postgresql+asyncpg://"
            f"{self.postgres_user}:{self.postgres_password}@"
            f"{self.postgres_server}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
