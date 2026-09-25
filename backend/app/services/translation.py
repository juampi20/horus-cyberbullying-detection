"""El router no sabe nada de redes ni de configuracion: solo ve TranslationService
y sus excepciones tipadas.
"""

import asyncio
import logging
import re
from collections.abc import Callable
from typing import Protocol

import requests
from deep_translator import GoogleTranslator, MyMemoryTranslator
from starlette.concurrency import run_in_threadpool

from app.core.config import settings

logger = logging.getLogger(__name__)


class TranslationError(Exception):
    """Fallo inesperado durante la traduccion (red, API, etc.)."""


class TranslationTimeoutError(TranslationError):
    """La traduccion no termino dentro del timeout configurado."""


class TranslationResult:
    """Traduccion final mas metadatos de confianza del pipeline."""

    def __init__(self, text: str, used_fallback: bool) -> None:
        self.text = text
        self.used_fallback = used_fallback


class TranslatorProtocol(Protocol):
    def translate(self, text: str) -> str: ...


TranslatorFactory = Callable[[], TranslatorProtocol]

_ERROR_MARKERS = re.compile(
    r"Error\s+\d+.*(?:Server Error|That's an error|try again later)"
    r"|Sorry\.\.\.|reCAPTCHA|captcha"
    r"|MYMEMORY WARNING|ALL AVAILABLE FREE TRANSLATIONS"
    r"|daily limit|usage limit|NO MATCH|no match found",
    re.IGNORECASE | re.DOTALL,
)


def _looks_like_error(text: str) -> bool:
    return bool(_ERROR_MARKERS.search(text))


class TranslationService:
    def __init__(
        self,
        translator_factories: list[TranslatorFactory],
        timeout: float,
    ) -> None:
        self._translator_factories = translator_factories
        self._timeout = timeout

    async def _try_translate(
        self, factory: TranslatorFactory, text: str
    ) -> tuple[str | None, str | None]:
        translator = factory()
        provider = type(translator).__name__
        try:
            translated = await asyncio.wait_for(
                run_in_threadpool(translator.translate, text),
                timeout=self._timeout,
            )
        except TimeoutError:
            logger.warning("Translation provider %s timed out", provider)
            return None, "timeout"
        except Exception:
            logger.exception("Translation provider %s raised an error", provider)
            return None, "error"
        if _looks_like_error(translated):
            logger.warning("Translation provider %s returned a non-translation response", provider)
            return None, "error"
        logger.info("Translation provider %s successfully translated", provider)
        return translated, None

    async def translate(self, text: str) -> TranslationResult:
        saw_timeout = False
        for index, factory in enumerate(self._translator_factories):
            translated, failure = await self._try_translate(factory, text)
            if translated is not None:
                return TranslationResult(
                    text=translated,
                    used_fallback=index > 0,
                )
            saw_timeout = saw_timeout or failure == "timeout"
            logger.info("Trying next translation provider")
        if saw_timeout:
            raise TranslationTimeoutError("Translation service timed out")
        raise TranslationError("All translation providers failed")


def _google_factory() -> TranslatorProtocol:
    return GoogleTranslator(source="auto", target="en")


def _mymemory_factory() -> TranslatorProtocol:
    return MyMemoryTranslator(source="spanish", target="english")


class DeeplApiTranslator:
    """Cliente directo de la API oficial de DeepL (plan Free).

    El wrapper de deep-translator envia la key como query param (auth_key) y
    DeepL ya no la acepta: exige el header `Authorization: DeepL-Auth-Key`.
    Esta clase replica la llamada que verifica la API (requests POST, JSON).
    """

    _BASE_URL = "https://api-free.deepl.com/v2/translate"

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    def translate(self, text: str) -> str:
        response = requests.post(
            self._BASE_URL,
            headers={
                "Authorization": f"DeepL-Auth-Key {self._api_key}",
                "Content-Type": "application/json",
            },
            json={
                "text": [text],
                "target_lang": "EN",
                "source_lang": "ES",
            },
            timeout=10,
        )
        if response.status_code != 200:
            raise TranslationError(f"DeepL API error (HTTP {response.status_code})")
        payload = response.json()
        return payload["translations"][0]["text"]


def _deepl_factory() -> TranslatorProtocol:
    if not settings.DEEPL_API_KEY:
        raise TranslationError("DeepL API key not configured")
    return DeeplApiTranslator(api_key=settings.DEEPL_API_KEY)


def _build_translator_factories() -> list[TranslatorFactory]:
    """DeepL (si hay key) primero; Google y MyMemory como fallbacks de red.

    DeepL es la fuente primaria: API oficial, calidad superior y mas estable
    que los gratuitos. Google es el primer respaldo y MyMemory la ultima red.
    Sin key de DeepL se mantiene el comportamiento original (Google + MyMemory).
    """
    factories: list[TranslatorFactory] = []
    if settings.DEEPL_API_KEY:
        factories.append(_deepl_factory)
    factories.append(_google_factory)
    factories.append(_mymemory_factory)
    return factories


translation_service = TranslationService(
    translator_factories=_build_translator_factories(),
    timeout=settings.MODEL_TIMEOUT_SECONDS,
)


def get_translation_service() -> TranslationService:
    return translation_service
