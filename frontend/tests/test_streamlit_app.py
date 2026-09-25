"""Behavior tests for pure helpers in frontend/streamlit_app.py."""

from __future__ import annotations

import api
import pytest


@pytest.fixture
def snake_case_converter(monkeypatch):
    """Imports streamlit_app without touching the backend during its import-time main()."""
    monkeypatch.setattr(api.ApiCalls, "healthcheck", lambda self, retries=3: True)
    monkeypatch.setattr(api, "fetch_models", lambda api_url: {"random_forest": {"f1": 0.83}})

    import streamlit_app

    return streamlit_app.to_snake_case


@pytest.mark.parametrize(
    "display_name,expected",
    [
        ("Random Forest", "random_forest"),
        ("XGBoost", "xgboost"),
        ("Logistic Regression", "logistic_regression"),
    ],
)
def test_to_snake_case_lowercases_and_replaces_spaces(
    snake_case_converter, display_name: str, expected: str
) -> None:
    assert snake_case_converter(display_name) == expected
