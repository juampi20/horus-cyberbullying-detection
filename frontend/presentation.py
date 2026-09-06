"""Helpers de presentacion puros para la UI de clasificacion de Horus."""

from __future__ import annotations

from collections import namedtuple
from typing import Any

from constants import CATEGORY_LABELS, UNCERTAINTY_MARGIN

# --- Presentacion en UI ---


def display_category(category: str) -> str:
    """Devuelve la etiqueta de UI en español para una categoria canonica."""
    return CATEGORY_LABELS.get(category, category)


def color_bg(category: str) -> str:
    """Devuelve un tag HTML <mark> con color de fondo para la categoria dada."""
    Color = namedtuple("Color", ["bg"])
    formatting = {
        "Bullying": Color(bg="#FF6347"),
        "No Bullying": Color(bg="#90EE90"),
        "Incierto": Color(bg="#F0AD4E"),
    }
    colors = formatting.get(category, None)
    if colors:
        return f"""<mark style="background-color: {colors.bg};">{category}</mark>"""
    return category


def metric_card(label: str, value: str) -> str:
    """HTML de una tarjeta metrica: valor grande + etiqueta debajo."""
    return (
        f'<div style="border:1px solid rgba(255,255,255,0.15); border-radius:8px;'
        f" padding:12px; text-align:center; background:rgba(255,255,255,0.04);"
        f' margin-bottom:8px;">'
        f'<div style="font-size:1.9rem; font-weight:700; line-height:1.2;">{value}</div>'
        f'<div style="font-size:0.85rem; opacity:0.7; margin-top:2px;">{label}</div>'
        f"</div>"
    )


def decision_rule_cards(margin: float = UNCERTAINTY_MARGIN) -> list[dict[str, str]]:
    """Devuelve las tarjetas de la regla de decision (etiqueta y rango) para la UI."""
    pct_low = (0.5 - margin) * 100
    pct_high = (0.5 + margin) * 100
    return [
        {"label": "No Bullying", "range": f"< {pct_low:.1f}%"},
        {"label": "Incierto", "range": f"{pct_low:.1f}% – {pct_high:.1f}%"},
        {"label": "Bullying", "range": f"> {pct_high:.1f}%"},
    ]


# --- Utilidades de texto ---


def is_short_text(text: str, min_words: int = 5) -> bool:
    """Devuelve True cuando el texto tiene menos de min_words palabras."""
    return len(text.split()) < min_words


def select_highlighted(
    results: list[dict[str, Any]],
    highlighted_model: str,
) -> dict[str, Any] | None:
    """Devuelve el resultado del modelo resaltado, o None si no se encuentra."""
    for result in results:
        if result.get("model") == highlighted_model:
            return result
    return None
