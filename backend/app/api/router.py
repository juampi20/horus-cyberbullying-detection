import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.services.metrics import MetricsFileError, MetricsService, get_metrics_service
from app.services.normalization import NormalizationService, get_normalization_service
from app.services.translation import (
    TranslationError,
    TranslationService,
    TranslationTimeoutError,
    get_translation_service,
)

from .models import ModelManager, get_model_manager
from .schemas import ClassResponse, HealthResponse, Input

logger = logging.getLogger(__name__)

classification_router = APIRouter()

ManagerDep = Annotated[ModelManager, Depends(get_model_manager)]
TranslationDep = Annotated[TranslationService, Depends(get_translation_service)]
MetricsDep = Annotated[MetricsService, Depends(get_metrics_service)]
NormalizationDep = Annotated[NormalizationService, Depends(get_normalization_service)]


@classification_router.get("/info")
async def get_models_info(metrics: MetricsDep) -> dict[str, dict[str, float]]:
    try:
        return metrics.get_metrics()
    except MetricsFileError as exc:
        raise HTTPException(status_code=500, detail=f"Metrics file not found: {exc}") from None


@classification_router.post("/predict", response_model=ClassResponse)
async def classify(
    item: Input,
    manager: ManagerDep,
    translator: TranslationDep,
    normalizer: NormalizationDep,
) -> ClassResponse:
    try:
        text_translated = await translator.translate(item.text)
    except TranslationTimeoutError:
        logger.error("Translation service timed out")
        raise HTTPException(
            status_code=503, detail="Translation service timeout, try again"
        ) from None
    except TranslationError:
        logger.exception("Translation service failed")
        raise HTTPException(status_code=503, detail="Translation service unavailable") from None

    text_normalized = normalizer.normalize(text_translated)

    try:
        category, confidence, inference_time_ms, model_version = manager.predict(
            text_normalized, item.model
        )
    except KeyError:
        logger.error("Requested model '%s' is not loaded", item.model)
        raise HTTPException(status_code=503, detail=f"Model '{item.model}' is not loaded") from None

    return ClassResponse(
        category=category,
        confidence=confidence,
        inference_time_ms=inference_time_ms,
        model_version=model_version,
    )


@classification_router.get("/healthcheck", response_model=HealthResponse)
async def healthcheck(manager: ManagerDep) -> HealthResponse:
    return HealthResponse(**manager.health_status())
