"""Black-box tests for the frontend/api.py HTTP client."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import api
import pytest
import requests

# ---------------------------------------------------------------------------
# make_predict / compare_text
# ---------------------------------------------------------------------------


def test_make_predict_non_200_raises_runtime_error_with_detail(monkeypatch) -> None:
    response = MagicMock()
    response.status_code = 422
    response.json.return_value = {"detail": "model not found"}
    monkeypatch.setattr(api.requests, "post", lambda **kwargs: response)

    with pytest.raises(RuntimeError, match="model not found"):
        api.ApiCalls().make_predict("Random Forest", "texto")


def test_make_predict_200_returns_parsed_payload(monkeypatch) -> None:
    response = MagicMock()
    response.status_code = 200
    response.text = json.dumps({"category": "Bullying", "confidence": 0.9})
    monkeypatch.setattr(api.requests, "post", lambda **kwargs: response)

    assert api.ApiCalls().make_predict("Random Forest", "texto") == {
        "category": "Bullying",
        "confidence": 0.9,
    }


def test_compare_text_non_200_raises_runtime_error_with_text_detail(monkeypatch) -> None:
    response = MagicMock()
    response.status_code = 500
    response.text = "internal error"
    response.json.side_effect = ValueError("not json")
    monkeypatch.setattr(api.requests, "post", lambda **kwargs: response)

    with pytest.raises(RuntimeError, match="internal error"):
        api.ApiCalls().compare_text("texto")


def test_compare_text_200_returns_parsed_payload(monkeypatch) -> None:
    response = MagicMock()
    response.status_code = 200
    response.text = json.dumps({"results": [], "used_fallback": False})
    monkeypatch.setattr(api.requests, "post", lambda **kwargs: response)

    assert api.ApiCalls().compare_text("texto") == {"results": [], "used_fallback": False}


# ---------------------------------------------------------------------------
# model_list
# ---------------------------------------------------------------------------


def test_model_list_invalid_json_returns_empty_dict(monkeypatch) -> None:
    response = MagicMock()
    response.text = "not-json"
    monkeypatch.setattr(api.requests, "get", lambda **kwargs: response)

    assert api.ApiCalls().model_list() == {}


def test_model_list_empty_text_returns_empty_dict(monkeypatch) -> None:
    response = MagicMock()
    response.text = ""
    monkeypatch.setattr(api.requests, "get", lambda **kwargs: response)

    assert api.ApiCalls().model_list() == {}


# ---------------------------------------------------------------------------
# healthcheck
# ---------------------------------------------------------------------------


def test_healthcheck_connection_error_returns_false(monkeypatch) -> None:
    calls = {"count": 0}

    def fail(**kwargs):
        calls["count"] += 1
        raise requests.exceptions.ConnectionError("refused")

    monkeypatch.setattr(api.requests, "get", fail)

    assert api.ApiCalls().healthcheck(retries=3) is False
    assert calls["count"] == 3
