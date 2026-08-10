import logging
import uuid
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse, Response

from .api.models import model_manager
from .api.router import classification_router
from .api.schemas import HealthResponse
from .core.config import app_configs, settings
from .core.logging import correlation_id_ctx, setup_logging
from .services.normalization import get_normalization_service

setup_logging(settings.LOG_LEVEL)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # spacy falla rápido si el modelo falta: conviene cargarlo primero
    normalization_service = get_normalization_service()
    normalization_service.load()
    logger.info("NormalizationService ready")

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
async def add_correlation_id(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
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
def docs_redirect() -> RedirectResponse:
    return RedirectResponse("/api/v1/docs")


app.include_router(classification_router, prefix="/api/v1/classification", tags=["classification"])

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
    # CLI: desde backend/: uvicorn app.main:app --reload --port 8000
