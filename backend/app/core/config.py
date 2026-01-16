"""
Application configuration using Pydantic Settings.
Follows Single Responsibility Principle - only handles configuration.
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    app_name: str = "AI Financial Manager"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "production"

    # Database
    db_user: str
    db_pass: str
    db_name: str
    db_host: str = "db"
    db_port: int = 5432

    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    encryption_key: str

    # Third Party APIs
    google_api_key: str
    monobank_api_url: str = "https://api.monobank.ua"

    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "https://yourapp.com"]

    # Rate Limiting
    rate_limit_per_minute: int = 60

    @property
    def database_url(self) -> str:
        """Construct PostgreSQL connection URL."""
        return f"postgresql://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/{self.db_name}"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            # Handle JSON string from .env
            import json
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # Handle comma-separated string
                return [origin.strip() for origin in v.split(",")]
        return v


# Singleton instance
settings = Settings()