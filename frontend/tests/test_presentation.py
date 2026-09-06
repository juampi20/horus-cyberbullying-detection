"""Unit tests for frontend/presentation.py pure functions."""

from __future__ import annotations

from constants import EXAMPLES, UNCERTAINTY_MARGIN
from presentation import (
    color_bg,
    decision_rule_cards,
    display_category,
    is_short_text,
    metric_card,
    select_highlighted,
)

# ---------------------------------------------------------------------------
# decision_rule_cards
# ---------------------------------------------------------------------------


def test_decision_rule_cards_menciona_los_tres_veredictos() -> None:
    cards = decision_rule_cards()
    labels = [c["label"] for c in cards]
    assert labels == ["No Bullying", "Incierto", "Bullying"]


def test_decision_rule_cards_default_margin() -> None:
    ranges = [c["range"] for c in decision_rule_cards()]
    assert "< 45.0%" in ranges[0]
    assert "45.0% – 55.0%" in ranges[1]
    assert "> 55.0%" in ranges[2]


def test_decision_rule_cards_custom_margin() -> None:
    ranges = [c["range"] for c in decision_rule_cards(0.1)]
    assert "< 40.0%" in ranges[0]
    assert "40.0% – 60.0%" in ranges[1]
    assert "> 60.0%" in ranges[2]


def test_decision_rule_cards_refleja_la_banda() -> None:
    middle = decision_rule_cards(0.02)[1]["range"]
    assert "48.0% – 52.0%" in middle
    middle_wide = decision_rule_cards(0.2)[1]["range"]
    assert "30.0% – 70.0%" in middle_wide


def test_decision_rule_cards_default_matches_constant() -> None:
    assert decision_rule_cards() == decision_rule_cards(UNCERTAINTY_MARGIN)


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
    assert is_short_text("Hola como estas") is True


def test_is_short_text_five_words_not_short() -> None:
    assert is_short_text("Hola como estas hoy vos") is False


def test_is_short_text_long_text() -> None:
    text = " ".join(["palabra"] * 20)
    assert is_short_text(text) is False


def test_is_short_text_custom_min_words() -> None:
    assert is_short_text("a b c", min_words=3) is False
    assert is_short_text("a b c", min_words=4) is True


# ---------------------------------------------------------------------------
# select_highlighted
# ---------------------------------------------------------------------------


def test_select_highlighted_found() -> None:
    results = [
        {"model": "Random Forest", "category": "Bullying", "confidence": 0.9},
        {"model": "SVM", "category": "Not Bullying", "confidence": 0.3},
    ]
    row = select_highlighted(results, "Random Forest")
    assert row is not None
    assert row["model"] == "Random Forest"
    assert row["category"] == "Bullying"


def test_select_highlighted_not_found() -> None:
    results = [{"model": "Random Forest", "category": "Bullying"}]
    row = select_highlighted(results, "XGBoost")
    assert row is None


def test_select_highlighted_empty_results() -> None:
    row = select_highlighted([], "Random Forest")
    assert row is None


# ---------------------------------------------------------------------------
# display_category
# ---------------------------------------------------------------------------


def test_display_category_not_bullying_en_espanol() -> None:
    assert display_category("Not Bullying") == "No Bullying"


def test_display_category_bullying_se_mantiene() -> None:
    assert display_category("Bullying") == "Bullying"


def test_display_category_incierto_se_mantiene() -> None:
    assert display_category("Uncertain") == "Incierto"


def test_display_category_desconocida_pasa_igual() -> None:
    assert display_category("OtraEtiqueta") == "OtraEtiqueta"


# ---------------------------------------------------------------------------
# EXAMPLES
# ---------------------------------------------------------------------------


def test_examples_has_12_items() -> None:
    assert len(EXAMPLES) == 12


def test_examples_include_uncertain_cases() -> None:
    assert "Tenes razon en algo, pero sos un poco molesto." in EXAMPLES
    assert "No entiendo por que te enojas tanto por todo." in EXAMPLES


def test_examples_are_strings() -> None:
    for ex in EXAMPLES:
        assert isinstance(ex, str)
        assert len(ex) > 0


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


def test_metric_card_contains_styling() -> None:
    result = metric_card("Confianza", "87.5%")
    assert "border-radius:8px" in result
    assert "font-size:1.9rem" in result
    assert "87.5%" in result
    assert "Confianza" in result
