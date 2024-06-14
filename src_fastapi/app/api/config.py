from typing import Any

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    CORS_ORIGINS: list[str] = ["*"]
    CORS_ORIGINS_REGEX: str | None = None
    CORS_HEADERS: list[str] = ["*"]

    APP_TITLE: str = "Horus API"
    APP_VERSION: str = "1"
    APP_DESCRIPTION: str = "Horus API for classification detection"


settings: BaseSettings = Config()

app_configs: dict[str, Any] = {
    "title": settings.APP_TITLE,
    "description": settings.APP_DESCRIPTION,
    "version": settings.APP_VERSION,
    "openapi_url": "/api/v1/openapi.json",
    "docs_url": "/api/v1/docs",
}
