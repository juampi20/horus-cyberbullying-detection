import pytest
from pydantic import ValidationError

from app.api.schemas import ClassResponse, HealthResponse, Input
from app.core.constants import SUPPORTED_MODELS


@pytest.mark.parametrize("model", SUPPORTED_MODELS)
def test_input_valid(model):
    item = Input(model=model, text="valid text")
    assert item.text == "valid text"
    assert item.model == model


def test_input_text_too_long_raises():
    with pytest.raises(ValidationError):
        Input(model="xgboost", text="a" * 501)


def test_input_empty_text_raises():
    with pytest.raises(ValidationError):
        Input(model="xgboost", text="")


def test_input_whitespace_text_raises():
    with pytest.raises(ValidationError):
        Input(model="xgboost", text="   ")


@pytest.mark.parametrize(
    "model",
    [
        "random forest",  # inválido: con espacio
        "does_not_exist",
        "Support Vector Machine (Linear Kernel)",
        "",
    ],
)
def test_input_invalid_model_raises(model):
    with pytest.raises(ValidationError):
        Input(model=model, text="valid text")


def test_input_too_long_within_500_ok():
    item = Input(model="xgboost", text="a" * 500)
    assert len(item.text) == 500


def test_class_response_fields():
    resp = ClassResponse(
        category="Bullying",
        confidence=0.85,
        inference_time_ms=12.3,
        model_version="abcdef12",
    )
    assert resp.category == "Bullying"
    assert resp.confidence == 0.85
    assert resp.inference_time_ms == 12.3
    assert resp.model_version == "abcdef12"


def test_health_response_defaults():
    resp = HealthResponse(status="healthy", models_loaded=7)
    assert resp.status == "healthy"
    assert resp.models_loaded == 7
    assert resp.missing_models is None
