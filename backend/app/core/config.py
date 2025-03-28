import secrets
from typing import Literal

from pydantic import (
    PostgresDsn,
    computed_field,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # set the model_config to use the .env file
    model_config = SettingsConfigDict(
        # Use top level .env file (one level above ./backend/)
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )

    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    # JWT token settings
    JWT_SECRET: str = "secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_TIMEDELTA: int = 30

    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    # Postges settings
    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(  # type: ignore[return-value]
            scheme="postgresql+psycopg2",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    # settings for a first user
    FIRST_SUPERUSER: str
    FIRST_SUPERUSER_PASSWORD: str
    FIRST_SUPERUSER_MAIL: str

    # settings for schema storage
    SCHEMA_STORAGE_TYPE: Literal["local"] = "local"
    SCHEMA_STORAGE_PATH: str

    # Backend settings
    BACKEND_IP: str
    BACKEND_PORT: int

    @computed_field  # type: ignore[prop-decorator]
    @property
    def BACKEND_URL(self) -> str:
        return f"{self.BACKEND_IP}:{self.BACKEND_PORT}"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def BACKEND_URL_API_V1(self) -> str:
        return f"{self.BACKEND_IP}:{self.BACKEND_PORT}{self.API_V1_STR}/"

    # Email settings
    # SMTP_TLS: bool = True
    # SMTP_SSL: bool = False
    # SMTP_PORT: int = 587
    # SMTP_HOST: str | None = None
    # SMTP_USER: str | None = None
    # SMTP_PASSWORD: str | None = None
    # # TODO: update type to EmailStr when sqlmodel supports it
    # EMAILS_FROM_EMAIL: str | None = None
    # EMAILS_FROM_NAME: str | None = None

    # @model_validator(mode="after")
    # def _set_default_emails_from(self) -> Self:
    #     if not self.EMAILS_FROM_NAME:
    #         self.EMAILS_FROM_NAME = self.PROJECT_NAME
    #     return self

    # EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48

    # @computed_field  # type: ignore[prop-decorator]
    # @property
    # def emails_enabled(self) -> bool:
    #     return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)


settings = Settings()  # type: ignore
