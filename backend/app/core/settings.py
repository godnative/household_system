from datetime import datetime, timedelta, timezone
from pathlib import Path
from functools import lru_cache
from urllib.parse import unquote, urlparse
import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BASE_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / '.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )

    app_env: str = Field(default='development', alias='APP_ENV')
    app_name: str = Field(default='household-system-api', alias='APP_NAME')
    debug: bool = Field(default=True, alias='DEBUG')
    database_url: str = Field(
        default='sqlite:///./household_system_web.db',
        alias='DATABASE_URL',
    )
    upload_dir: str = Field(default='backend/app/static/uploads', alias='UPLOAD_DIR')
    static_system_dir: str = Field(default='backend/app/static/system', alias='STATIC_SYSTEM_DIR')
    frontend_origin: str = Field(default='http://127.0.0.1:5173', alias='FRONTEND_ORIGIN')
    frontend_dist_dir: str = Field(default='frontend/dist', alias='FRONTEND_DIST_DIR')
    serve_frontend: bool = Field(default=False, alias='SERVE_FRONTEND')
    runtime_base_dir: str = Field(default='', alias='RUNTIME_BASE_DIR')
    access_token_expire_minutes: int = Field(default=60 * 12, alias='ACCESS_TOKEN_EXPIRE_MINUTES')
    jwt_secret_key: str = Field(default='change-me-in-production', alias='JWT_SECRET_KEY')
    jwt_algorithm: str = Field(default='HS256', alias='JWT_ALGORITHM')

    @property
    def access_token_expire_delta(self) -> timedelta:
        return timedelta(minutes=self.access_token_expire_minutes)

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == 'production'

    @property
    def resolved_runtime_base_dir(self) -> Path:
        configured_dir = self.runtime_base_dir.strip()
        if configured_dir:
            return Path(configured_dir).expanduser().resolve()

        if os.name == 'nt' and self.is_production:
            local_app_data = os.environ.get('LOCALAPPDATA')
            if local_app_data:
                return Path(local_app_data).resolve() / 'HouseholdSystemWeb'

        return PROJECT_ROOT.resolve()

    def _resolve_path(self, raw_path: str) -> Path:
        path = Path(raw_path)
        if path.is_absolute():
            return path.resolve()
        return (self.resolved_runtime_base_dir / path).resolve()

    @property
    def resolved_upload_dir(self) -> Path:
        return self._resolve_path(self.upload_dir)

    @property
    def resolved_frontend_dist_dir(self) -> Path:
        return self._resolve_path(self.frontend_dist_dir)

    @property
    def resolved_database_path(self) -> Path | None:
        if not self.database_url.startswith('sqlite'):
            return None

        parsed = urlparse(self.database_url)
        database_path = unquote(parsed.path or '')
        if parsed.netloc and database_path:
            database_path = f'//{parsed.netloc}{database_path}'

        if not database_path:
            return None

        if database_path == ':memory:':
            return None

        normalized_path = database_path
        while normalized_path.startswith('//'):
            normalized_path = normalized_path[1:]

        path = Path(normalized_path)
        if not path.is_absolute():
            path = (self.resolved_runtime_base_dir / path).resolve()
        return path

    @property
    def issued_at(self) -> datetime:
        return datetime.now(timezone.utc)


@lru_cache
def get_settings() -> Settings:
    return Settings()
