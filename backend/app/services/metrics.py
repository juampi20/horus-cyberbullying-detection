"""Métricas de los modelos leídas desde un CSV. El servicio centraliza la
lectura del archivo y el mapeo a dict; si el archivo falta o el CSV es
inválido, lanza MetricsFileError y el router solo decide la respuesta HTTP.
"""

import csv
import logging
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)


class MetricsFileError(Exception):
    """El archivo de métricas no existe o no se pudo parsear."""


class MetricsService:
    def __init__(self, metrics_path: Path) -> None:
        self._metrics_path = metrics_path

    def get_metrics(self) -> dict[str, dict[str, float]]:
        try:
            with open(self._metrics_path) as f:
                reader = csv.DictReader(f)
                models_info: dict[str, dict[str, float]] = {}
                for row in reader:
                    models_info[row["Model"]] = {
                        "precision": float(row["Precision"]),
                        "f1": float(row["F1"]),
                        "recall": float(row["Recall"]),
                        "accuracy": float(row["Accuracy"]),
                    }
            return models_info
        except FileNotFoundError as exc:
            logger.error("Metrics file not found: %s", self._metrics_path)
            raise MetricsFileError(str(self._metrics_path)) from exc
        except (csv.Error, KeyError, ValueError) as exc:
            logger.exception("Metrics file is invalid: %s", self._metrics_path)
            raise MetricsFileError("invalid metrics file") from exc


# Singleton inyectado por el router via Depends; la ruta se fija al levantar
metrics_service = MetricsService(metrics_path=settings.METRICS_PATH)


def get_metrics_service() -> MetricsService:
    return metrics_service
