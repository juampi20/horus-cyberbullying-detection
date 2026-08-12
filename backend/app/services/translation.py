"""El router no sabe nada de redes ni de configuración: solo ve TranslationService
y sus excepciones tipadas.
"""

import asyncio
import logging
from typing import Protocol

from deep_translator import GoogleTranslator
from starlette.concurrency import run_in_threadpool

from app.core.config import settings

logger = logging.getLogger(__name__)


class TranslationError(Exception):
    """Fallo inesperado durante la traducción (red, API, etc.)."""


class TranslationTimeoutError(TranslationError):
    """La traducción no terminó dentro del timeout configurado."""


class TranslatorProtocol(Protocol):
    def translate(self, text: str) -> str: ...


class TranslatorFactory(Protocol):
    def __call__(self, source: str, target: str) -> TranslatorProtocol: ...


class TranslationService:
    def __init__(self, translator_cls: TranslatorFactory, timeout: float) -> None:
        self._translator_cls = translator_cls
        self._timeout = timeout

    async def translate(self, text: str) -> str:
        translator = self._translator_cls(source="auto", target="en")
        try:
            return await asyncio.wait_for(
                run_in_threadpool(translator.translate, text),
                timeout=self._timeout,
            )
        except TimeoutError:
            logger.error("Translation service timed out")
            raise TranslationTimeoutError("Translation service timed out") from None
        except Exception as exc:
            logger.exception("Translation service failed")
            raise TranslationError("Translation service failed") from exc


# Singleton inyectado por el router vía Depends; el timeout se fija al levantar
translation_service = TranslationService(
    translator_cls=GoogleTranslator,
    timeout=settings.MODEL_TIMEOUT_SECONDS,
)


def get_translation_service() -> TranslationService:
    return translation_service
