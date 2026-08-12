"""Unit tests for frontend/consensus.py pure functions."""

from __future__ import annotations

from consensus import (
    classify_consensus,
    compute_consensus,
    compute_weighted_consensus,
    f1_weights,
)
from constants import UNCERTAINTY_MARGIN

# ---------------------------------------------------------------------------
# compute_consensus
# ---------------------------------------------------------------------------


def test_compute_consensus_all_bullying() -> None:
    results = [{"model": f"m{i}", "category": "Bullying"} for i in range(7)]
    votes, majority, pct = compute_consensus(results)
    assert votes == 7
    assert majority == "Bullying"
    assert pct == 100.0


def test_compute_consensus_all_not_bullying() -> None:
    results = [{"model": f"m{i}", "category": "Not Bullying"} for i in range(7)]
    votes, majority, pct = compute_consensus(results)
    assert votes == 0
    assert majority == "Not Bullying"
    assert pct == 100.0


def test_compute_consensus_split() -> None:
    results = [{"model": "m0", "category": "Bullying"}] * 4 + [
        {"model": f"m{i}", "category": "Not Bullying"} for i in range(1, 4)
    ]
    votes, majority, pct = compute_consensus(results)
    assert votes == 4
    assert majority == "Bullying"
    assert abs(pct - 57.14) < 0.1


def test_compute_consensus_empty() -> None:
    votes, majority, pct = compute_consensus([])
    assert votes == 0
    assert majority == "Not Bullying"
    assert pct == 0.0


# ---------------------------------------------------------------------------
# compute_weighted_consensus
# ---------------------------------------------------------------------------


def test_weighted_consensus_all_bullying() -> None:
    results = [{"model": f"m{i}", "category": "Bullying"} for i in range(7)]
    weights = {f"m{i}": 0.5 + i * 0.05 for i in range(7)}
    score, majority, pct = compute_weighted_consensus(results, weights)
    assert score == 1.0
    assert majority == "Bullying"
    assert pct == 100.0


def test_weighted_consensus_all_not_bullying() -> None:
    results = [{"model": f"m{i}", "category": "Not Bullying"} for i in range(7)]
    weights = {f"m{i}": 0.5 + i * 0.05 for i in range(7)}
    score, majority, pct = compute_weighted_consensus(results, weights)
    assert score == 0.0
    assert majority == "Not Bullying"
    assert pct == 100.0


def test_weighted_consensus_high_f1_bullying_dominates() -> None:
    results = [{"model": "random_forest", "category": "Bullying"}] + [
        {"model": f"low{i}", "category": "Not Bullying"} for i in range(6)
    ]
    weights = {"random_forest": 0.832}
    weights.update({f"low{i}": 0.10 for i in range(6)})
    score, majority, pct = compute_weighted_consensus(results, weights)
    assert 0.0 < score < 1.0
    assert majority == "Bullying"
    assert abs(pct - 600 / 7) < 0.1


def test_weighted_consensus_high_f1_not_bullying_dominates() -> None:
    results = [{"model": "random_forest", "category": "Not Bullying"}] + [
        {"model": f"low{i}", "category": "Bullying"} for i in range(6)
    ]
    weights = {"random_forest": 0.832}
    weights.update({f"low{i}": 0.10 for i in range(6)})
    score, majority, pct = compute_weighted_consensus(results, weights)
    assert 0.0 < score < 1.0
    assert majority == "Not Bullying"
    assert abs(pct - 600 / 7) < 0.1


def test_weighted_consensus_missing_weight_uses_zero() -> None:
    results = [
        {"model": "known", "category": "Bullying"},
        {"model": "unknown", "category": "Not Bullying"},
    ]
    weights = {"known": 0.8}
    score, majority, pct = compute_weighted_consensus(results, weights)
    assert score == 1.0
    assert majority == "Bullying"
    assert pct == 50.0


def test_weighted_consensus_empty() -> None:
    score, majority, pct = compute_weighted_consensus([], {"m0": 0.5})
    assert score == 0.0
    assert majority == "Not Bullying"
    assert pct == 0.0


# ---------------------------------------------------------------------------
# f1_weights
# ---------------------------------------------------------------------------


def test_f1_weights_mejor_modelo_pesa_amplificacion_veces_el_peor() -> None:
    scores = {"peor": 0.78, "medio": 0.80, "mejor": 0.83}
    weights = f1_weights(scores, amplification=4.0)
    assert weights["peor"] == 1.0
    assert weights["mejor"] == 4.0
    assert 1.0 < weights["medio"] < 4.0


def test_f1_weights_conserva_orden_monotono() -> None:
    scores = {"a": 0.78, "b": 0.80, "c": 0.83, "d": 0.79}
    weights = f1_weights(scores)
    ordered_names = sorted(weights, key=weights.get, reverse=True)  # type: ignore[arg-type]
    assert ordered_names == ["c", "b", "d", "a"]


def test_f1_weights_f1s_identicos_pesan_igual() -> None:
    scores = {"a": 0.81, "b": 0.81, "c": 0.81}
    weights = f1_weights(scores, amplification=5.0)
    assert weights == {"a": 1.0, "b": 1.0, "c": 1.0}


def test_f1_weights_vacio_devuelve_vacio() -> None:
    assert f1_weights({}) == {}


def test_f1_weights_default_amplification() -> None:
    assert f1_weights({"peor": 0.78, "mejor": 0.83})["mejor"] == 5.0


# ---------------------------------------------------------------------------
# classify_consensus
# ---------------------------------------------------------------------------


def test_classify_consensus_clear_bullying() -> None:
    assert classify_consensus(0.6) == "Bullying"


def test_classify_consensus_clear_not_bullying() -> None:
    assert classify_consensus(0.4) == "Not Bullying"


def test_classify_consensus_near_boundary_high() -> None:
    assert classify_consensus(0.52) == "Uncertain"


def test_classify_consensus_near_boundary_low() -> None:
    assert classify_consensus(0.48) == "Uncertain"


def test_classify_consensus_exact_decision_boundary() -> None:
    assert classify_consensus(0.5) == "Uncertain"


def test_classify_consensus_upper_boundary() -> None:
    assert classify_consensus(0.55) == "Uncertain"


def test_classify_consensus_lower_boundary() -> None:
    assert classify_consensus(0.45) == "Uncertain"


def test_classify_consensus_just_outside_band() -> None:
    assert classify_consensus(0.5501) == "Bullying"
    assert classify_consensus(0.4499) == "Not Bullying"


def test_classify_consensus_custom_margin() -> None:
    assert classify_consensus(0.53, margin=0.1) == "Uncertain"
    assert classify_consensus(0.61, margin=0.1) == "Bullying"
    assert classify_consensus(0.39, margin=0.1) == "Not Bullying"
    assert classify_consensus(0.4, margin=0.1) == "Uncertain"


def test_uncertainty_margin_constant_default() -> None:
    assert UNCERTAINTY_MARGIN == 0.05
