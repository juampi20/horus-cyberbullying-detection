import hashlib

import pytest

from app.api.constants import SUPPORTED_MODELS
from app.api.models import ModelManager


@pytest.fixture
def manager(fake_models_dir, fake_joblib):
    m = ModelManager()
    m.load_models()
    return m


def test_load_models_discovers_all(manager):
    assert set(manager.loaded_names) == set(SUPPORTED_MODELS)
    assert len(manager._models) == len(SUPPORTED_MODELS)


@pytest.mark.parametrize(
    "fake_models_dir, expected, expected_loaded",
    [
        pytest.param(list(SUPPORTED_MODELS), "healthy", len(SUPPORTED_MODELS), id="all"),
        pytest.param(
            list(SUPPORTED_MODELS[:-1]),
            "degraded",
            len(SUPPORTED_MODELS) - 1,
            id="one-missing",
        ),
        pytest.param([], "unhealthy", 0, id="none"),
    ],
    indirect=["fake_models_dir"],
)
def test_health_status(fake_models_dir, fake_joblib, expected, expected_loaded):
    m = ModelManager()
    m.load_models()
    status = m.health_status()
    assert status["status"] == expected
    assert status["models_loaded"] == expected_loaded


def test_health_degraded_lists_missing(manager, fake_models_dir, tmp_path):
    (fake_models_dir / "xgboost.pkl").unlink()
    m = ModelManager()
    m.load_models()
    status = m.health_status()
    assert status["status"] == "degraded"
    assert "xgboost" in status["missing_models"]


@pytest.mark.parametrize("fake_models_dir", [[]], indirect=True)
def test_health_unhealthy_empty(fake_models_dir, fake_joblib):
    m = ModelManager()
    m.load_models()
    status = m.health_status()
    assert status["status"] == "unhealthy"
    assert status["models_loaded"] == 0
    assert status["missing_models"] == list(SUPPORTED_MODELS)


def test_predict_returns_tuple(manager):
    category, confidence, inference_time_ms, version = manager.predict("some text", "xgboost")
    assert category == "Bullying"
    assert confidence == 0.85
    assert isinstance(inference_time_ms, float)
    assert inference_time_ms >= 0
    assert len(version) == 8


def test_predict_version_is_sha8(manager, fake_models_dir):
    version = manager._models["xgboost"]["version"]
    expected = hashlib.sha256((fake_models_dir / "xgboost.pkl").read_bytes()).hexdigest()[:8]
    assert version == expected
    assert len(version) == 8


def test_predict_unknown_model_raises_keyerror(manager):
    with pytest.raises(KeyError):
        manager.predict("some text", "does_not_exist")
