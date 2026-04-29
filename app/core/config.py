import secrets
from typing import Annotated, Any, Literal

from pydantic import AnyUrl, BeforeValidator, EmailStr, PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(v: Any) -> list[str] | Any:
    """
    Allow env formats:
    BACKEND_CORS_ORIGINS=http://a.com,http://b.com
    BACKEND_CORS_ORIGINS=["http://a.com"]
    """
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",") if i.strip()]

    if isinstance(v, (list, str)):
        return v

    raise ValueError(v)


class Settings(BaseSettings):
    """Application configuration"""

    model_config = SettingsConfigDict(
        # `.env.prod` takes priority over `.env`
        env_file=(".env", ".env.local", ".env.prod"),
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

    # Basic App Info
    PROJECT_NAME: str = "FastAPI App"
    VERSION: str = "1.0.0"
    PORT: int = 8000
    FRONTEND_HOST: str = "http://localhost:5173"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)

    # Logger
    LOGGER_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    # CORS
    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def assemble_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]

    # Postgres
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None
    REDIS_URL: str | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def REDIS_DSN(self) -> str:
        """
        If REDIS_URL is provided, use it directly,
        otherwise build from components.
        """
        if self.REDIS_URL:
            return self.REDIS_URL

        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # Github OAuth
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""

    # Observability
    SLOW_QUERY_THRESHOLD_MS: int = 1000  # Log queries slower than this (ms)
    METRICS_ENABLED: bool = True

    # OpenTelemetry
    OTEL_ENABLED: bool = False
    OTEL_EXPORTER_OTLP_ENDPOINT: str | None = None
    OTEL_EXPORTER_OTLP_INSECURE: bool = True

    FIRST_SUPERUSER: EmailStr = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: str = "change_this"


settings = Settings()
