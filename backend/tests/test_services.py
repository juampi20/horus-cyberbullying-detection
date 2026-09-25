"""Tests unitarios de la capa de servicios (app/services).

Se testea cada servicio de forma aislada, con el I/O mockeado (traductor fake,
CSV de tmp_path, pipelines de spaCy reales cuando el modelo esta instalado).
"""

import asyncio
import time
from pathlib import Path

import pytest
import spacy

from app.core.config import settings
from app.services.metrics import MetricsFileError, MetricsService
from app.services.normalization import NormalizationService
from app.services.translation import (
    TranslationError,
    TranslationProvider,
    TranslationService,
    TranslationTimeoutError,
    TranslatorFactory,
    _deepl_factory,
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


class ErrorTextTranslator:
    """Simula el bloqueo silencioso de Google: HTTP 200 con HTML de error."""

    def __init__(self, source="auto", target="en"):
        pass

    def translate(self, text: str) -> str:
        return (
            "Error 500 (Server Error)!!1500.That's an error."
            "There was an error. Please try again later."
        )


class MyMemoryWarningTranslator:
    """Simula MyMemory agotado: HTTP 200 con warning de limite diario."""

    def __init__(self, source="auto", target="en"):
        pass

    def translate(self, text: str) -> str:
        return (
            "MYMEMORY WARNING: YOU USED ALL AVAILABLE FREE TRANSLATIONS FOR TODAY."
            " Visit https://mymemory.translated.net/doc/usagelimits.php"
        )


def _factory_of(translator_cls: type) -> callable:
    return lambda: translator_cls()


def _factory_returning(text: str) -> callable:
    class FixedResponseTranslator:
        def __init__(self, source="auto", target="en"):
            pass

        def translate(self, inner_text: str) -> str:
            return text

    return _factory_of(FixedResponseTranslator)


def _provider(name: str, factory: TranslatorFactory) -> TranslationProvider:
    """Envuelve una factory con la identidad estable del proveedor."""
    return TranslationProvider(name=name, factory=factory)


def test_translation_service_success() -> None:
    service = TranslationService(
        translator_providers=[_provider("stub", _factory_of(StubTranslator))],
        timeout=1.0,
    )
    result = asyncio.run(service.translate("hello"))
    assert result.text == "translated hello"
    assert result.used_fallback is False
    assert result.provider == "stub"


def test_translation_reports_google_when_google_is_first() -> None:
    """Regresion: Google en el indice 0 se reporta como Google, nunca DeepL."""
    service = TranslationService(
        translator_providers=[
            _provider("google", _factory_of(StubTranslator)),
            _provider("mymemory", _factory_of(StubTranslator)),
        ],
        timeout=1.0,
    )
    result = asyncio.run(service.translate("hello"))
    assert result.provider == "google"
    assert result.used_fallback is False


def test_translation_service_timeout() -> None:
    service = TranslationService(
        translator_providers=[_provider("stub", _factory_of(SlowTranslator))],
        timeout=0.1,
    )
    with pytest.raises(TranslationTimeoutError):
        asyncio.run(service.translate("hello"))


def test_translation_service_error() -> None:
    service = TranslationService(
        translator_providers=[_provider("stub", _factory_of(FailingTranslator))],
        timeout=1.0,
    )
    with pytest.raises(TranslationError):
        asyncio.run(service.translate("hello"))


def test_translation_fallback_when_first_fails() -> None:
    service = TranslationService(
        translator_providers=[
            _provider("deepl", _factory_of(FailingTranslator)),
            _provider("google", _factory_of(StubTranslator)),
        ],
        timeout=1.0,
    )
    result = asyncio.run(service.translate("hello"))
    assert result.text == "translated hello"
    assert result.used_fallback is True
    assert result.provider == "google"


def test_translation_fallback_when_first_returns_error_text() -> None:
    service = TranslationService(
        translator_providers=[
            _provider("google", _factory_of(ErrorTextTranslator)),
            _provider("mymemory", _factory_of(StubTranslator)),
        ],
        timeout=1.0,
    )
    result = asyncio.run(service.translate("hello"))
    assert result.text == "translated hello"
    assert result.used_fallback is True
    assert result.provider == "mymemory"


def test_translation_fallback_when_first_returns_mymemory_warning() -> None:
    service = TranslationService(
        translator_providers=[
            _provider("mymemory", _factory_of(MyMemoryWarningTranslator)),
            _provider("google", _factory_of(StubTranslator)),
        ],
        timeout=1.0,
    )
    result = asyncio.run(service.translate("hello"))
    assert result.text == "translated hello"
    assert result.used_fallback is True
    assert result.provider == "google"


def test_translation_all_providers_fail() -> None:
    service = TranslationService(
        translator_providers=[
            _provider("google", _factory_of(FailingTranslator)),
            _provider("mymemory", _factory_of(ErrorTextTranslator)),
        ],
        timeout=1.0,
    )
    with pytest.raises(TranslationError):
        asyncio.run(service.translate("hello"))


def test_translation_all_providers_timeout_raises_timeout() -> None:
    service = TranslationService(
        translator_providers=[
            _provider("google", _factory_of(SlowTranslator)),
            _provider("mymemory", _factory_of(SlowTranslator)),
        ],
        timeout=0.1,
    )
    with pytest.raises(TranslationTimeoutError):
        asyncio.run(service.translate("hello"))


def test_deepl_provider_posts_to_official_api(monkeypatch) -> None:
    monkeypatch.setattr(settings, "DEEPL_API_KEY", "test-key")
    captured: dict = {}

    class FakeResponse:
        status_code = 200

        def json(self) -> dict:
            return {"translations": [{"text": "translated text"}]}

    def fake_post(url, headers, json, timeout):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        return FakeResponse()

    monkeypatch.setattr("app.services.translation.requests.post", fake_post)

    translator = _deepl_factory()
    assert translator.translate("hola") == "translated text"
    assert captured["url"] == "https://api-free.deepl.com/v2/translate"
    assert captured["headers"]["Authorization"] == "DeepL-Auth-Key test-key"


def test_deepl_provider_non_200_raises_translation_error(monkeypatch) -> None:
    monkeypatch.setattr(settings, "DEEPL_API_KEY", "test-key")

    class FakeResponse:
        status_code = 403

    def fake_post(url, headers, json, timeout):
        return FakeResponse()

    monkeypatch.setattr("app.services.translation.requests.post", fake_post)

    translator = _deepl_factory()
    with pytest.raises(TranslationError):
        translator.translate("hola")


def test_deepl_factory_without_key_raises_translation_error(monkeypatch) -> None:
    monkeypatch.setattr(settings, "DEEPL_API_KEY", "")
    with pytest.raises(TranslationError):
        _deepl_factory()


@pytest.mark.parametrize(
    "error_text",
    [
        "Sorry...",
        "reCAPTCHA verification required",
        "captcha verification required",
        "You reached the daily limit",
        "usage limit exceeded",
        "NO MATCH",
    ],
)
def test_translation_fallback_when_provider_returns_error_marker(error_text: str) -> None:
    service = TranslationService(
        translator_providers=[
            _provider("google", _factory_returning(error_text)),
            _provider("mymemory", _factory_of(StubTranslator)),
        ],
        timeout=1.0,
    )
    result = asyncio.run(service.translate("hello"))
    assert result.text == "translated hello"
    assert result.used_fallback is True
    assert result.provider == "mymemory"


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
    reason="en_core_web_sm no esta instalado en este entorno",
)
def test_normalization_service_load_and_normalize() -> None:
    service = NormalizationService()
    service.load()
    assert service.is_loaded
    assert service.normalize("I am not good at this") == "not_good"
