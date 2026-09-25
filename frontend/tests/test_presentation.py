"""Unit tests for frontend/presentation.py pure functions."""

from __future__ import annotations

import pytest
from presentation import (
    color_bg,
    decision_rule_cards,
    display_category,
    is_short_text,
    metric_card,
)

# ---------------------------------------------------------------------------
# decision_rule_cards
# ---------------------------------------------------------------------------


def test_decision_rule_cards_menciona_los_tres_veredictos() -> None:
    cards = decision_rule_cards()
    labels = [c["label"] for c in cards]
    assert labels == ["No Bullying", "Incierto", "Bullying"]


@pytest.mark.parametrize(
    "margin,expected_ranges",
    [
        (None, ["< 45.0%", "45.0% – 55.0%", "> 55.0%"]),
        (0.1, ["< 40.0%", "40.0% – 60.0%", "> 60.0%"]),
        (0.02, ["< 48.0%", "48.0% – 52.0%", "> 52.0%"]),
        (0.2, ["< 30.0%", "30.0% – 70.0%", "> 70.0%"]),
    ],
)
def test_decision_rule_cards_reflect_margin_band(
    margin: float | None, expected_ranges: list[str]
) -> None:
    cards = decision_rule_cards() if margin is None else decision_rule_cards(margin)
    assert [c["range"] for c in cards] == expected_ranges


# ---------------------------------------------------------------------------
# is_short_text
# ---------------------------------------------------------------------------


def test_is_short_text_single_word() -> None:
    assert is_short_text("Hola") is True


def test_is_short_text_empty() -> None:
    assert is_short_text("") is True


def test_is_short_text_whitespace_only() -> None:
    assert is_short_text("   ") is True


def test_is_short_text_four_words() -> None:
    assert is_short_text("Hola como estas hoy") is True


def test_is_short_text_five_words_not_short() -> None:
    assert is_short_text("Hola como estas hoy vos") is False


def test_is_short_text_long_text() -> None:
    text = " ".join(["palabra"] * 20)
    assert is_short_text(text) is False


def test_is_short_text_custom_min_words() -> None:
    assert is_short_text("a b c", min_words=3) is False
    assert is_short_text("a b c", min_words=4) is True


# ---------------------------------------------------------------------------
# display_category
# ---------------------------------------------------------------------------


def test_display_category_not_bullying_en_espanol() -> None:
    assert display_category("Not Bullying") == "No Bullying"


def test_display_category_incierto_se_mantiene() -> None:
    assert display_category("Uncertain") == "Incierto"


def test_display_category_desconocida_pasa_igual() -> None:
    assert display_category("OtraEtiqueta") == "OtraEtiqueta"


# ---------------------------------------------------------------------------
# color_bg
# ---------------------------------------------------------------------------


def test_color_bg_bullying_returns_mark_tag() -> None:
    result = color_bg("Bullying")
    assert "<mark" in result
    assert "FF6347" in result
    assert "Bullying" in result


def test_color_bg_no_bullying_returns_mark_tag() -> None:
    result = color_bg("No Bullying")
    assert "<mark" in result
    assert "90EE90" in result
    assert "No Bullying" in result


def test_color_bg_incierto_returns_mark_tag() -> None:
    result = color_bg("Incierto")
    assert "<mark" in result
    assert "F0AD4E" in result
    assert "Incierto" in result


def test_color_bg_unknown_category_passthrough() -> None:
    result = color_bg("OtraEtiqueta")
    assert result == "OtraEtiqueta"
    assert "<mark" not in result


# ---------------------------------------------------------------------------
# metric_card
# ---------------------------------------------------------------------------


def test_metric_card_returns_div_html() -> None:
    result = metric_card("F1", "0.82")
    assert "<div" in result
    assert "0.82" in result
    assert "F1" in result
