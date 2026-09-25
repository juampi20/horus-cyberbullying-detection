import pytest
from pydantic import ValidationError

from app.api.schemas import Input


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
        "random forest",  # invalido: con espacio
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
