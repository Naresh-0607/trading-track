from functools import lru_cache
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Trade Track API"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost/trade_track"
    jwt_secret_key: str = "development-only-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    allowed_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.replace("postgres://", "postgresql+asyncpg://", 1) if value.startswith("postgres://") else value
            value = value.replace("postgresql://", "postgresql+asyncpg://", 1) if value.startswith("postgresql://") else value
            if not value.startswith("postgresql+asyncpg://"):
                return value
            parts = urlsplit(value)
            query = []
            for key, item in parse_qsl(parts.query, keep_blank_values=True):
                if key == "channel_binding":
                    continue
                query.append(("ssl" if key == "sslmode" else key, item))
            value = urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))
        return value

    @property
    def allowed_origins_list(self) -> list[str]:
        return [item.strip() for item in self.allowed_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
