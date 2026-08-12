from typing import Literal, get_args

from pydantic import BaseModel, Field, field_validator

from app.core.constants import SUPPORTED_MODELS

# mypy exige valores explícitos en Literal[...]; la lista se mantiene en sync con
# core.constants.SUPPORTED_MODELS y se valida en runtime con el assert de abajo.
MODEL_NAME = Literal[
    "gradient_boosting",
    "logistic_regression",
    "multinomial_naive_bayes",
    "neural_network",
    "random_forest",
    "support_vector_machine_(linear_kernel)",
    "xgboost",
]

assert set(get_args(MODEL_NAME)) == set(SUPPORTED_MODELS)  # noqa: S101


class Input(BaseModel):
    model: MODEL_NAME
    text: str = Field(..., max_length=500)

    @field_validator("text")
    @classmethod
    def text_not_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("text must not be empty")
        return value


class ClassResponse(BaseModel):
    category: str
    confidence: float
    inference_time_ms: float
    model_version: str


class CompareItem(BaseModel):
    text: str = Field(..., max_length=500)

    @field_validator("text")
    @classmethod
    def text_not_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("text must not be empty")
        return value


class CompareResult(BaseModel):
    model: str
    category: str
    confidence: float
    inference_time_ms: float
    model_version: str


class CompareResponse(BaseModel):
    results: list[CompareResult]


class HealthResponse(BaseModel):
    status: str
    models_loaded: int
    missing_models: list[str] | None = None
