import sys
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.constants import SUPPORTED_MODELS  # noqa: E402


class FakeModel:
    def predict(self, X):
        return [1]

    def predict_proba(self, X):
        return [[0.2, 0.85]]


class FakeGoogleTranslator:
    def __init__(self, source="auto", target="en"):
        pass

    def translate(self, text):
        return "translated text"


@pytest.fixture
def fake_joblib(monkeypatch):
    """Evita tocar los modelos reales: joblib.load devuelve un FakeModel."""

    monkeypatch.setattr("app.api.models.joblib.load", lambda path: FakeModel())


@pytest.fixture
def fake_models_dir(tmp_path, monkeypatch, request):
    """Crea *.pkl falsos en un tmp_path y lo apunta como MODELS_DIR.

    Se puede parametrizar con la lista de nombres de modelo a crear.
    """

    names = getattr(request, "param", None)
    if names is None:
        names = SUPPORTED_MODELS
    for name in names:
        (tmp_path / f"{name}.pkl").write_bytes(b"fake-pickle-data")
    monkeypatch.setattr("app.core.config.settings.MODELS_DIR", tmp_path)
    return tmp_path


@pytest.fixture(autouse=True)
def mock_translator(monkeypatch):
    """No toca red: el singleton de traduccion usa un traductor fake."""

    from app.core.config import settings
    from app.services.translation import TranslationService

    fake = TranslationService(
        translator_cls=FakeGoogleTranslator,
        timeout=settings.MODEL_TIMEOUT_SECONDS,
    )
    monkeypatch.setattr("app.services.translation.translation_service", fake)


@pytest.fixture
def client(fake_models_dir, fake_joblib):
    from starlette.testclient import TestClient

    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def client_without_xgboost(tmp_path, monkeypatch, fake_joblib):
    """Client cuyo ModelManager cargo todos los modelos salvo xgboost."""

    from starlette.testclient import TestClient

    from app.main import app

    for name in SUPPORTED_MODELS:
        if name != "xgboost":
            (tmp_path / f"{name}.pkl").write_bytes(b"fake-pickle-data")
    monkeypatch.setattr("app.core.config.settings.MODELS_DIR", tmp_path)

    with TestClient(app) as test_client:
        yield test_client
