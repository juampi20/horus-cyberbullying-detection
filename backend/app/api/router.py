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
from .schemas import (
    ClassResponse,
    CompareItem,
    CompareResponse,
    CompareResult,
    HealthResponse,
    Input,
)

logger = logging.getLogger(__name__)

classification_router = APIRouter()

ManagerDep = Annotated[ModelManager, Depends(get_model_manager)]
TranslationDep = Annotated[TranslationService, Depends(get_translation_service)]
MetricsDep = Annotated[MetricsService, Depends(get_metrics_service)]
NormalizationDep = Annotated[NormalizationService, Depends(get_normalization_service)]


async def prepare_text(
    item: Input | CompareItem,
    translator: TranslationService,
    normalizer: NormalizationService,
) -> str:
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

    return normalizer.normalize(text_translated)


@classification_router.get("/info")
async def get_models_info(metrics: MetricsDep) -> dict[str, dict[str, float]]:
    try:
        return metrics.get_metrics()
    except MetricsFileError:
        raise HTTPException(status_code=500, detail="Metrics file is unavailable") from None


@classification_router.post("/predict", response_model=ClassResponse)
async def classify(
    item: Input,
    manager: ManagerDep,
    translator: TranslationDep,
    normalizer: NormalizationDep,
) -> ClassResponse:
    text_normalized = await prepare_text(item, translator, normalizer)

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


@classification_router.post("/compare", response_model=CompareResponse)
async def compare(
    item: CompareItem,
    manager: ManagerDep,
    translator: TranslationDep,
    normalizer: NormalizationDep,
) -> CompareResponse:
    text_normalized = await prepare_text(item, translator, normalizer)
    results = [CompareResult(**result) for result in manager.predict_all(text_normalized)]
    return CompareResponse(results=results)


@classification_router.get("/healthcheck", response_model=HealthResponse)
async def healthcheck(manager: ManagerDep) -> HealthResponse:
    return HealthResponse(**manager.health_status())
