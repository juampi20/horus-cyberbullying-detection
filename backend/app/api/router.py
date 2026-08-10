import asyncio
import csv
import logging
from typing import Annotated, Any

from deep_translator import GoogleTranslator
from fastapi import APIRouter, Depends, HTTPException
from starlette.concurrency import run_in_threadpool

from app.core.config import settings
from app.services.normalization import NormalizationService, get_normalization_service

from .models import ModelManager, get_model_manager
from .schemas import ClassResponse, HealthResponse, Input

logger = logging.getLogger(__name__)

classification_router = APIRouter()

ManagerDep = Annotated[ModelManager, Depends(get_model_manager)]
NormalizationDep = Annotated[NormalizationService, Depends(get_normalization_service)]


# Información de los modelos
@classification_router.get("/info")
async def get_models_info() -> dict[str, dict[str, Any]]:
    try:
        with open(settings.METRICS_PATH) as f:
            reader = csv.DictReader(f)
            models_info: dict[str, dict[str, Any]] = {}
            for row in reader:
                models_info[row["Model"]] = {
                    "precision": float(row["Precision"]),
                    "f1": float(row["F1"]),
                    "recall": float(row["Recall"]),
                    "accuracy": float(row["Accuracy"]),
                }
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=500, detail=f"Metrics file not found: {settings.METRICS_PATH}"
        ) from exc
    return models_info


@classification_router.post("/predict", response_model=ClassResponse)
async def classify(item: Input, manager: ManagerDep, normalizer: NormalizationDep) -> ClassResponse:
    try:
        text_translated = await asyncio.wait_for(
            run_in_threadpool(GoogleTranslator(source="auto", target="en").translate, item.text),
            timeout=settings.MODEL_TIMEOUT_SECONDS,
        )
    except TimeoutError:
        logger.error("Translation service timed out")
        raise HTTPException(
            status_code=503, detail="Translation service timeout, try again"
        ) from None
    except Exception:
        logger.exception("Translation service failed")
        raise HTTPException(status_code=503, detail="Translation service unavailable") from None

    text_normalized = normalizer.normalize(str(text_translated))

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
