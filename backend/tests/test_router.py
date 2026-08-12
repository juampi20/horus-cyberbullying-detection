import time
from pathlib import Path

from app.services.metrics import metrics_service
from app.services.translation import TranslationService

PREDICT_URL = "/api/v1/classification/predict"
COMPARE_URL = "/api/v1/classification/compare"


def test_healthcheck_healthy(client):
    resp = client.get("/healthcheck")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["models_loaded"] == 7
    assert data["missing_models"] is None


def test_router_healthcheck_healthy(client):
    resp = client.get("/api/v1/classification/healthcheck")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


def test_predict_valid(client):
    resp = client.post(PREDICT_URL, json={"model": "xgboost", "text": "you are worthless"})
    assert resp.status_code == 200
    data = resp.json()
    assert set(data.keys()) == {"category", "confidence", "inference_time_ms", "model_version"}
    assert data["category"] == "Bullying"
    assert data["confidence"] == 0.85
    assert data["inference_time_ms"] >= 0
    assert len(data["model_version"]) == 8


def test_predict_not_bullying(client, monkeypatch):
    from app.api.models import model_manager

    model = model_manager._models["xgboost"]["model"]
    monkeypatch.setattr(model, "predict", lambda X: [0])
    monkeypatch.setattr(model, "predict_proba", lambda X: [[0.9, 0.1]])

    resp = client.post(PREDICT_URL, json={"model": "xgboost", "text": "have a nice day"})
    assert resp.status_code == 200
    assert resp.json()["category"] == "Not Bullying"
    assert resp.json()["confidence"] == 0.1


def test_predict_text_too_long_422(client):
    resp = client.post(PREDICT_URL, json={"model": "xgboost", "text": "a" * 501})
    assert resp.status_code == 422


def test_predict_empty_text_422(client):
    resp = client.post(PREDICT_URL, json={"model": "xgboost", "text": ""})
    assert resp.status_code == 422


def test_predict_unknown_model_422(client):
    resp = client.post(PREDICT_URL, json={"model": "does_not_exist", "text": "hello"})
    assert resp.status_code == 422


def test_predict_spaced_model_name_422(client):
    resp = client.post(PREDICT_URL, json={"model": "random forest", "text": "hello"})
    assert resp.status_code == 422


def test_predict_missing_model_503(client_without_xgboost):
    resp = client_without_xgboost.post(PREDICT_URL, json={"model": "xgboost", "text": "hello"})
    assert resp.status_code == 503


def test_predict_translation_timeout_503(client, monkeypatch):
    class SlowTranslator:
        def __init__(self, source="auto", target="en"):
            pass

        def translate(self, text):
            time.sleep(0.5)
            return "translated text"

    monkeypatch.setattr(
        "app.services.translation.translation_service",
        TranslationService(translator_cls=SlowTranslator, timeout=0.1),
    )

    resp = client.post(PREDICT_URL, json={"model": "xgboost", "text": "hello"})
    assert resp.status_code == 503
    assert "timeout" in resp.json()["detail"].lower()


def test_predict_translation_unavailable_503(client, monkeypatch):
    class FailingTranslator:
        def __init__(self, source="auto", target="en"):
            pass

        def translate(self, text):
            raise RuntimeError("boom")

    monkeypatch.setattr(
        "app.services.translation.translation_service",
        TranslationService(translator_cls=FailingTranslator, timeout=10.0),
    )

    resp = client.post(PREDICT_URL, json={"model": "xgboost", "text": "hello"})
    assert resp.status_code == 503
    assert "unavailable" in resp.json()["detail"].lower()


def test_compare_ok(client):
    resp = client.post(COMPARE_URL, json={"text": "you are worthless"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["failed_models"] == []
    results = body["results"]
    assert len(results) == 7
    expected_keys = {
        "model",
        "category",
        "confidence",
        "inference_time_ms",
        "model_version",
    }
    expected_models = {
        "gradient_boosting",
        "logistic_regression",
        "multinomial_naive_bayes",
        "neural_network",
        "random_forest",
        "support_vector_machine_(linear_kernel)",
        "xgboost",
    }
    for result in results:
        assert set(result.keys()) == expected_keys
    assert {result["model"] for result in results} == expected_models


def test_compare_partial_failure(client, monkeypatch):
    from app.api.models import model_manager

    original_predict = model_manager.predict

    def flaky_predict(text, model_name):
        if model_name == "xgboost":
            raise RuntimeError("boom")
        return original_predict(text, model_name)

    monkeypatch.setattr(model_manager, "predict", flaky_predict)
    resp = client.post(COMPARE_URL, json={"text": "you are worthless"})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["results"]) == 6
    assert body["failed_models"] == ["xgboost"]


def test_compare_text_too_long_422(client):
    resp = client.post(COMPARE_URL, json={"text": "a" * 501})
    assert resp.status_code == 422


def test_compare_empty_text_422(client):
    resp = client.post(COMPARE_URL, json={"text": ""})
    assert resp.status_code == 422


def test_compare_translation_timeout_503(client, monkeypatch):
    class SlowTranslator:
        def __init__(self, source="auto", target="en"):
            pass

        def translate(self, text):
            time.sleep(0.5)
            return "translated text"

    monkeypatch.setattr(
        "app.services.translation.translation_service",
        TranslationService(translator_cls=SlowTranslator, timeout=0.1),
    )

    resp = client.post(COMPARE_URL, json={"text": "hello"})
    assert resp.status_code == 503
    assert "timeout" in resp.json()["detail"].lower()


def test_compare_translation_unavailable_503(client, monkeypatch):
    class FailingTranslator:
        def __init__(self, source="auto", target="en"):
            pass

        def translate(self, text):
            raise RuntimeError("boom")

    monkeypatch.setattr(
        "app.services.translation.translation_service",
        TranslationService(translator_cls=FailingTranslator, timeout=10.0),
    )

    resp = client.post(COMPARE_URL, json={"text": "hello"})
    assert resp.status_code == 503
    assert "unavailable" in resp.json()["detail"].lower()


def test_info_ok(client):
    resp = client.get("/api/v1/classification/info")
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, dict)
    assert "XGBoost" in body
    for metric in ("precision", "recall", "f1", "accuracy"):
        assert metric in body["XGBoost"]


def test_info_missing_csv_500(client, monkeypatch):
    monkeypatch.setattr(metrics_service, "_metrics_path", Path("/nonexistent/models_results.csv"))
    resp = client.get("/api/v1/classification/info")
    assert resp.status_code == 500
