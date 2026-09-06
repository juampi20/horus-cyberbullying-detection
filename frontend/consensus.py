"""Logica de consenso pura para la clasificacion de Horus."""

from __future__ import annotations

from typing import Any

from constants import UNCERTAINTY_MARGIN, WEIGHT_AMPLIFICATION

# --- Logica de consenso ---


def f1_weights(
    f1_scores: dict[str, float], amplification: float = WEIGHT_AMPLIFICATION
) -> dict[str, float]:
    """Devuelve el peso de voto de cada modelo: el mejor F1 pesa `amplification`× el peor."""
    if not f1_scores:
        return {}
    min_f1 = min(f1_scores.values())
    max_f1 = max(f1_scores.values())
    span = max_f1 - min_f1
    if span <= 0:
        return {name: 1.0 for name in f1_scores}
    weights: dict[str, float] = {}
    for name, f1 in f1_scores.items():
        position = (f1 - min_f1) / span
        weights[name] = 1.0 + position * (amplification - 1.0)
    return weights


def compute_consensus(
    results: list[dict[str, Any]],
) -> tuple[int, str, float]:
    """Devuelve (bullying_votes, majority_category, agreement_pct)."""
    if not results:
        return 0, "Not Bullying", 0.0
    bullying_votes = sum(1 for result in results if result.get("category") == "Bullying")
    total = len(results)
    majority = "Bullying" if bullying_votes >= total / 2 else "Not Bullying"
    agreement_pct = max(bullying_votes, total - bullying_votes) / total * 100
    return bullying_votes, majority, agreement_pct


def compute_weighted_consensus(
    results: list[dict[str, Any]],
    weights: dict[str, float],
) -> tuple[float, str, float]:
    """Devuelve (weighted_bullying_score, majority_category, agreement_pct)."""
    if not results:
        return 0.0, "Not Bullying", 0.0
    total_weight = 0.0
    bullying_weight = 0.0
    for result in results:
        weight = weights.get(str(result.get("model")), 0.0)
        total_weight += weight
        if result.get("category") == "Bullying":
            bullying_weight += weight
    if total_weight <= 0:
        return 0.0, "Not Bullying", 0.0
    weighted_bullying_score = bullying_weight / total_weight
    majority = "Bullying" if weighted_bullying_score >= 0.5 else "Not Bullying"
    _, _, agreement_pct = compute_consensus(results)
    return weighted_bullying_score, majority, agreement_pct


def classify_consensus(
    weighted_bullying_score: float,
    margin: float = UNCERTAINTY_MARGIN,
) -> str:
    """Devuelve "Bullying", "Not Bullying" o "Uncertain" segun el score ponderado."""
    if weighted_bullying_score > 0.5 + margin:
        return "Bullying"
    if weighted_bullying_score < 0.5 - margin:
        return "Not Bullying"
    return "Uncertain"
