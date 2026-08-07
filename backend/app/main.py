import contextvars
import json
import logging
import logging.config
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from .api.config import app_configs, settings
from .api.models import model_manager
from .api.router import classification_router
from .api.schemas import HealthResponse

correlation_id_ctx: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "correlation_id", default=None
)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "correlation_id": correlation_id_ctx.get(),
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {"json": {"()": JsonFormatter}},
        "handlers": {"default": {"class": "logging.StreamHandler", "formatter": "json"}},
        "root": {"handlers": ["default"], "level": settings.LOG_LEVEL},
        "loggers": {
            name: {"handlers": ["default"], "level": settings.LOG_LEVEL, "propagate": False}
            for name in ("uvicorn", "uvicorn.error", "uvicorn.access")
        },
    }
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    model_manager.load_models()
    app.state.model_manager = model_manager
    logger.info(
        "ModelManager ready",
        extra={"status": model_manager.health_status()},
    )
    yield


app = FastAPI(**app_configs, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ORIGINS_REGEX,
    allow_credentials=True,
    allow_methods=("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"),
    allow_headers=settings.CORS_HEADERS,
)


@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    token = correlation_id_ctx.set(request_id)
    try:
        logger.info(
            "Incoming request",
            extra={"method": request.method, "path": request.url.path},
        )
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        correlation_id_ctx.reset(token)


@app.get("/healthcheck", include_in_schema=False, response_model=HealthResponse)
async def healthcheck() -> HealthResponse:
    return HealthResponse(**app.state.model_manager.health_status())


@app.get("/", include_in_schema=False)
def docs_redirect():
    return RedirectResponse("/api/v1/docs")


app.include_router(classification_router, prefix="/api/v1/classification", tags=["classification"])

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
    # CLI: uvicorn backend.app.main:app --reload --port 8000
