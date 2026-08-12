"""Normalización de texto previa al modelado. Ver notebooks/00_normalize.ipynb."""

import html
import re
from collections.abc import Iterable

import spacy
from spacy.tokens import Token
from unidecode import unidecode

from app.core.constants import CONTRACTIONS, LEET, NEGATION_WORDS, SLANG


# --- Limpieza regex: solo caracteres, sin NLP ---
def clean_text(text: str) -> str:
    text = text.lower()
    text = html.unescape(text)
    expanded = (
        CONTRACTIONS.get(word, SLANG.get(word, LEET.get(word, word))) for word in text.split()
    )
    text = " ".join(expanded)
    text = re.sub(r"[^\x00-\x7F]+", "", text)  # fuera de ASCII
    text = re.sub(r"[a-z0-9._+-]+@[a-z0-9._+-]+\.[a-z]+", "", text)  # correos
    text = re.sub(r"http\S+", "", text)  # links
    text = re.sub(r"@\S+", "", text)  # menciones
    text = re.sub(r"#\S+", "", text)  # etiquetas
    text = re.sub(r"\brt\b", " ", text)  # RT (borde de palabra)
    text = re.sub(r"[^a-zA-Z]", " ", text)  # solo letras
    return " ".join(unidecode(word) for word in text.split())


def normalize_elongation(word: str) -> str:
    """sooooo -> so."""
    return re.sub(r"(.)\1{2,}", r"\1", word)


def keep_token(token: Token) -> bool:
    """Las negaciones se conservan aunque sean stopwords de spaCy."""
    if token.text in NEGATION_WORDS:
        return True
    return (
        not (token.is_punct or token.is_stop or token.like_num)
        and len(token) > 2
        and len(set(token.text)) > 1
    )


def mark_negation(tokens: Iterable[str]) -> list[str]:
    """not good -> not_good."""
    output_tokens: list[str] = []
    negated = False
    for word in tokens:
        if word in NEGATION_WORDS:
            negated = True
            continue
        output_tokens.append(("not_" if negated else "") + word)
        negated = False
    if negated:
        output_tokens.append("not")
    return output_tokens


class NormalizationService:
    """Limpia, filtra, lematiza y marca negaciones; los pipelines se cargan con load()."""

    def __init__(self) -> None:
        self._tokenizer: spacy.Language | None = None
        self._lemmatizer: spacy.Language | None = None
        self._loaded = False

    def load(self) -> None:
        if self._loaded:
            return
        self._lemmatizer = spacy.load("en_core_web_sm", disable=["ner"])
        self._tokenizer = spacy.load(
            "en_core_web_sm",
            disable=["tagger", "parser", "ner", "attribute_ruler", "lemmatizer"],
        )
        self._loaded = True

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def normalize(self, text: str) -> str:
        if not self.is_loaded:
            raise RuntimeError("NormalizationService not loaded")
        tokenizer = self._tokenizer
        lemmatizer = self._lemmatizer
        if tokenizer is None or lemmatizer is None:
            raise RuntimeError("NormalizationService not loaded")
        cleaned = clean_text(text)
        tokens = [
            normalize_elongation(token.text) for token in tokenizer(cleaned) if keep_token(token)
        ]
        lemmas = [token.lemma_ for token in lemmatizer(" ".join(tokens))]
        return " ".join(mark_negation(lemmas))


normalization_service = NormalizationService()


def get_normalization_service() -> NormalizationService:
    return normalization_service
