"""Cliente HTTP del backend de Horus para la UI de Streamlit."""

from __future__ import annotations

import json
import logging
import os
from typing import Any

import requests
import streamlit as st

logger = logging.getLogger(__name__)


class ApiCalls:
    def __init__(self, url: str = os.getenv("API_URL", default="http://localhost:8000/")) -> None:
        self.url = url
        self.headers = {"Content-Type": "application/json"}

    def healthcheck(self, retries: int = 3) -> bool:
        endpoint = self.url + "healthcheck"
        for _ in range(retries):
            try:
                response = requests.get(url=endpoint, timeout=10)
                if response.status_code == 200:
                    return True
            except requests.exceptions.ConnectionError:
                pass
        return False

    def model_list(self) -> dict[str, Any]:
        endpoint = self.url + "api/v1/classification/info"
        try:
            models = requests.get(url=endpoint, timeout=10)
        except requests.exceptions.RequestException:
            logger.exception("Failed to fetch models from %s", endpoint)
            return {}

        if models.text:
            try:
                return json.loads(models.text)
            except json.JSONDecodeError:
                logger.error("Response is not a valid JSON document")
                return {}
        else:
            logger.error("Response is empty")
            return {}

    def make_predict(self, model: str, text: str) -> dict[str, Any]:
        endpoint = self.url + "api/v1/classification/predict"

        payload = {"model": model.lower().replace(" ", "_"), "text": text}
        result = requests.post(
            url=endpoint,
            headers=self.headers,
            data=json.dumps(payload),
            timeout=10,
        )
        if result.status_code != 200:
            try:
                detail = result.json()["detail"]
            except (ValueError, KeyError):
                detail = result.text
            logger.error("Predict failed (HTTP %s): %s", result.status_code, detail)
            raise RuntimeError(f"Server error ({result.status_code}): {detail}") from None
        return json.loads(result.text)

    def compare_text(self, text: str) -> dict[str, Any]:
        endpoint = self.url + "api/v1/classification/compare"

        payload = {"text": text}
        result = requests.post(
            url=endpoint,
            headers=self.headers,
            data=json.dumps(payload),
            timeout=10,
        )
        if result.status_code != 200:
            try:
                detail = result.json()["detail"]
            except (ValueError, KeyError):
                detail = result.text
            logger.error("Compare failed (HTTP %s): %s", result.status_code, detail)
            raise RuntimeError(f"Server error ({result.status_code}): {detail}") from None
        return json.loads(result.text)


@st.cache_data(ttl=300, show_spinner=False)
def fetch_models(api_url: str) -> dict[str, Any]:
    """Consulta el catálogo de modelos al backend y lo cachea 5 minutos."""
    return ApiCalls(url=api_url).model_list()
