import hashlib
import logging
import time

import joblib

from app.core.config import settings
from app.core.constants import CATEGORY_BULLYING, CATEGORY_NOT_BULLYING, SUPPORTED_MODELS

logger = logging.getLogger(__name__)


class ModelManager:
    """Los modelos faltantes o corruptos no crashean la carga."""

    def __init__(self) -> None:
        self._models: dict[str, dict] = {}

    def load_models(self) -> None:
        self._models = {}
        for pkl_path in sorted(settings.MODELS_DIR.glob("*.pkl")):
            name = pkl_path.stem
            try:
                model = joblib.load(pkl_path)
            except Exception:  # noqa: BLE001, S110 - un modelo corrupto no debe crashear el resto
                logger.warning("Skipping unloadable model %s", pkl_path)
                continue
            version = hashlib.sha256(pkl_path.read_bytes()).hexdigest()[:8]
            self._models[name] = {"model": model, "version": version}

    @property
    def loaded_names(self) -> set[str]:
        return set(self._models.keys())

    def health_status(self) -> dict:
        missing = [m for m in SUPPORTED_MODELS if m not in self._models]
        total = len(self._models)
        if total == 0:
            return {"status": "unhealthy", "models_loaded": 0, "missing_models": missing}
        if not missing:
            return {"status": "healthy", "models_loaded": total, "missing_models": None}
        return {"status": "degraded", "models_loaded": total, "missing_models": missing}

    def predict(self, text: str, model_name: str) -> tuple[str, float, float, str]:
        if model_name not in self._models:
            raise KeyError(model_name)
        model = self._models[model_name]["model"]
        start = time.perf_counter()
        prediction = model.predict([text])
        probabilities = model.predict_proba([text])
        end = time.perf_counter()
        inference_time_ms = (end - start) * 1000
        category = CATEGORY_BULLYING if prediction[0] == 1 else CATEGORY_NOT_BULLYING
        confidence = round(float(probabilities[0][1]), 2)
        version = self._models[model_name]["version"]
        return category, confidence, inference_time_ms, version

    def predict_all(self, text: str) -> list[dict[str, object]]:
        results = []
        for name in sorted(self._models):
            try:
                category, confidence, inference_time_ms, version = self.predict(text, name)
            except Exception:  # noqa: BLE001, S110 - un modelo que falle no debe tumbar el lote
                logger.warning("Skipping failed model %s", name)
                continue
            results.append(
                {
                    "model": name,
                    "category": category,
                    "confidence": confidence,
                    "inference_time_ms": inference_time_ms,
                    "model_version": version,
                }
            )
        return results


# Singleton inyectado por el router vía Depends y apuntado por el lifespan de main
model_manager = ModelManager()


def get_model_manager() -> ModelManager:
    return model_manager
