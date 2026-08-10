"""Tests unitarios de la capa de servicios (app/services).

Se testea cada servicio de forma aislada, con el I/O mockeado (traductor fake,
CSV de tmp_path, pipelines de spaCy reales cuando el modelo está instalado).
"""

import asyncio
import time
from pathlib import Path

import pytest
import spacy

from app.services.metrics import MetricsFileError, MetricsService
from app.services.normalization import NormalizationService
from app.services.translation import (
    TranslationError,
    TranslationService,
    TranslationTimeoutError,
)

VALID_CSV = (
    "Model,Precision,Recall,F1,Accuracy\n"
    "XGBoost,0.908856183836819,0.7129835932752684,0.7990919409761634,0.7812384130515387\n"
)


# --- TranslationService ---


class StubTranslator:
    def __init__(self, source="auto", target="en"):
        pass

    def translate(self, text: str) -> str:
        return f"translated {text}"


class SlowTranslator:
    def __init__(self, source="auto", target="en"):
        pass

    def translate(self, text: str) -> str:
        time.sleep(0.5)
        return "translated text"


class FailingTranslator:
    def __init__(self, source="auto", target="en"):
        pass

    def translate(self, text: str) -> str:
        raise RuntimeError("boom")


def test_translation_service_success() -> None:
    service = TranslationService(translator_cls=StubTranslator, timeout=1.0)
    assert asyncio.run(service.translate("hello")) == "translated hello"


def test_translation_service_timeout() -> None:
    service = TranslationService(translator_cls=SlowTranslator, timeout=0.1)
    with pytest.raises(TranslationTimeoutError):
        asyncio.run(service.translate("hello"))


def test_translation_service_error() -> None:
    service = TranslationService(translator_cls=FailingTranslator, timeout=1.0)
    with pytest.raises(TranslationError):
        asyncio.run(service.translate("hello"))


# --- MetricsService ---


def test_metrics_service_ok(tmp_path) -> None:
    path = tmp_path / "metrics.csv"
    path.write_text(VALID_CSV)
    service = MetricsService(metrics_path=path)
    assert service.get_metrics()["XGBoost"] == {
        "precision": 0.908856183836819,
        "f1": 0.7990919409761634,
        "recall": 0.7129835932752684,
        "accuracy": 0.7812384130515387,
    }


def test_metrics_service_file_not_found() -> None:
    service = MetricsService(metrics_path=Path("/nonexistent/metrics.csv"))
    with pytest.raises(MetricsFileError):
        service.get_metrics()


def test_metrics_service_invalid_csv(tmp_path) -> None:
    path = tmp_path / "metrics.csv"
    path.write_text("Model,Precision,Recall,F1,Accuracy\nXGBoost,not_a_number,0.7,0.8,0.9\n")
    service = MetricsService(metrics_path=path)
    with pytest.raises(MetricsFileError):
        service.get_metrics()


# --- NormalizationService ---


def test_normalization_service_not_loaded_raises() -> None:
    service = NormalizationService()
    with pytest.raises(RuntimeError):
        service.normalize("hello")


@pytest.mark.skipif(
    not spacy.util.is_package("en_core_web_sm"),
    reason="en_core_web_sm no está instalado en este entorno",
)
def test_normalization_service_load_and_normalize() -> None:
    service = NormalizationService()
    service.load()
    assert service.is_loaded
    assert service.normalize("I am not good at this") == "not_good"
