"""Tests de paridad del pipeline de normalización (app/services/normalization.py).

Los casos de esperado replican los outputs guardados en la celda de smoke test
de notebooks/00_normalize.ipynb: el backend debe producir EXACTAMENTE el mismo
resultado que el pipeline de entrenamiento.
"""

import pytest

from app.services.normalization import normalization_service

# Los pipelines se cargan una sola vez por sesión de tests (load() es idempotente)
normalization_service.load()


def normalize(text: str) -> str:
    return normalization_service.normalize(text)


# Cada caso: (texto crudo, salida esperada del notebook)
PARITY_CASES = [
    # Limpieza de ruido: RT (word boundary), URLs, menciones, hashtags, emojis
    ("RT I'm learning Python and      I'm enjoying it. :) >.<", "learn python enjoy"),
    ("I have a website at https://www.example.com with discounts.", "website discount"),
    ("What do you think about the new product from @company? #opinions", "think new product"),
    ("10 ways to improve your mental health. #health #wellness 🧘", "way improve mental health"),
    # Contracciones + marcado de negación
    ("I am not good at this", "not_good"),
    ("this is not funny", "not_funny"),
    ("don't talk to me", "not_talk"),
    ("I can't believe it", "not_believe"),
    ("I do not like you", "not_like"),
    # Elongación
    ("sooooo good", "so good"),
    ("noooo", "not"),
    ("yesssss", "yes"),
    ("hiiiii how are you", "hi"),
    # Tokens sin señal (un único carácter distinto) se descartan
    ("zzzz", ""),
]


@pytest.mark.parametrize(("text", "expected"), PARITY_CASES)
def test_normalize_parity_with_notebook(text: str, expected: str) -> None:
    assert normalize(text) == expected


def test_normalize_slang_and_leetspeak() -> None:
    # aint -> are not (alimenta la negación); h8 -> hate (leetspeak del dataset)
    assert normalize("aint funny at all") == "not_funny"
    assert normalize("i h8 you") == "hate"


def test_normalize_html_entities() -> None:
    # html.unescape ocurre ANTES de la limpieza regex: &amp; -> & -> se elimina
    assert normalize("i &amp; my friend") == "friend"


def test_normalize_negation_not_swallowed_by_stopwords() -> None:
    # not/no/never son stopwords de spaCy; keep_token las conserva a propósito.
    # "give" también es stopword, así que "never give up" deja solo "never"
    # huérfano -> mark_negation lo conserva como "not".
    assert normalize("never give up") == "not"
    assert normalize("I do not") == "not"
