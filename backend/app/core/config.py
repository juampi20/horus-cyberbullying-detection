from pathlib import Path
from typing import Any

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MODELS_DIR: Path = Path(__file__).parents[2] / "app" / "api" / "models"
    METRICS_PATH: Path = Path(__file__).parents[2] / "app" / "api" / "models" / "models_results.csv"

    CORS_ORIGINS: list[str] = ["*"]
    CORS_ORIGINS_REGEX: str | None = None
    CORS_HEADERS: list[str] = ["*"]

    APP_TITLE: str = "Horus API"
    APP_VERSION: str = "1"
    APP_DESCRIPTION: str = "Horus API for classification detection"

    LOG_LEVEL: str = "INFO"
    MODEL_TIMEOUT_SECONDS: float = 10.0


settings: Settings = Settings()

app_configs: dict[str, Any] = {
    "title": settings.APP_TITLE,
    "description": settings.APP_DESCRIPTION,
    "version": settings.APP_VERSION,
    "openapi_url": "/api/v1/openapi.json",
    "docs_url": "/api/v1/docs",
}
