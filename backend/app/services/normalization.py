"""Normalización de texto previa al modelado. Ver notebooks/00_normalize.ipynb."""

import html
import re
from collections.abc import Iterable

import spacy
from spacy.tokens import Token
from unidecode import unidecode

# --- Expansión de contracciones ---
CONTRACTIONS = {
    "don't": "do not",
    "dont": "do not",
    "can't": "cannot",
    "cant": "cannot",
    "won't": "will not",
    "wont": "will not",
    "isn't": "is not",
    "isnt": "is not",
    "aren't": "are not",
    "arent": "are not",
    "didn't": "did not",
    "didnt": "did not",
    "doesn't": "does not",
    "doesnt": "does not",
    "wasn't": "was not",
    "wasnt": "was not",
    "weren't": "were not",
    "werent": "were not",
    "haven't": "have not",
    "havent": "have not",
    "hasn't": "has not",
    "hasnt": "has not",
    "hadn't": "had not",
    "hadnt": "had not",
    "i'm": "i am",
    "i've": "i have",
    "i'll": "i will",
    "you're": "you are",
    "you've": "you have",
    "we're": "we are",
    "they're": "they are",
    "it's": "it is",
    "that's": "that is",
    "what's": "what is",
    "there's": "there is",
}

# Slang de redes sociales -> forma canónica (u = you, idk = i do not know...)
SLANG = {
    # Pronombres/verbos abreviados
    "u": "you",
    "ur": "your",
    "r": "are",
    "n": "and",
    "y": "why",
    "k": "ok",
    "ya": "you",
    "yall": "you all",
    # Contracciones
    "gonna": "going to",
    "wanna": "want to",
    "gotta": "got to",
    "lemme": "let me",
    "gimme": "give me",
    "imma": "i am going to",
    "kinda": "kind of",
    "sorta": "sort of",
    "dunno": "do not know",
    # Abreviaturas
    "idk": "i do not know",
    "idc": "i do not care",
    "ngl": "not going to lie",
    "tbh": "to be honest",
    "imo": "in my opinion",
    "imho": "in my humble opinion",
    "smh": "shake my head",
    "btw": "by the way",
    "rn": "right now",
    "fr": "for real",
    "af": "as fuck",
    "afk": "away from keyboard",
    "bc": "because",
    "cuz": "because",
    "bcoz": "because",
    "cos": "because",
    "tho": "though",
    "pls": "please",
    "plz": "please",
    "thx": "thanks",
    "wut": "what",
    "wat": "what",
    "sup": "what is up",
    "lol": "laugh out loud",
    "omg": "oh my god",
    "brb": "be right back",
    # Chatspeak
    "aint": "are not",
    "da": "the",
    "dat": "that",
    "dis": "this",
    "dem": "them",
    "dese": "these",
    "dose": "those",
    "dey": "they",
    "dere": "there",
    "kno": "know",
    "luv": "love",
    "gud": "good",
    "wuz": "was",
    "wus": "was",
    "pic": "picture",
    "pics": "pictures",
    "cmon": "come on",
    "hbu": "how about you",
}

# Leetspeak (b4 = before, h8 = hate)
LEET = {
    "b4": "before",
    "2day": "today",
    "2nite": "tonight",
    "2night": "tonight",
    "2mrrw": "tomorrow",
    "2morrow": "tomorrow",
    "2mrw": "tomorrow",
    "2morw": "tomorrow",
    "str8": "straight",
    "str8p": "straight",
    "some1": "someone",
    "sum1": "someone",
    "any1": "anyone",
    "no1": "no one",
    "every1": "everyone",
    "h8": "hate",
    "4got": "forgot",
    "gr8": "great",
    "in2": "into",
    "2getha": "together",
    "2gether": "together",
    "2do": "to do",
    "2b": "to be",
    "4ever": "forever",
    "2much": "too much",
    "4da": "for the",
    "l8r": "later",
    "m8": "mate",
    "w8": "wait",
    "4u": "for you",
    "2u": "to you",
    "2go": "to go",
    "2me": "to me",
    "4me": "for me",
    "2know": "to know",
    "2see": "to see",
    "2have": "to have",
    "2make": "to make",
    "2give": "to give",
    "2stop": "to stop",
    "2come": "to come",
    "2show": "to show",
    "2bully": "to bully",
    "n00b": "noob",
    "bl00d": "blood",
    "bl00dy": "bloody",
    "br00t4l": "brutal",
    "r4pe": "rape",
    "k1ll3d": "killed",
    "sh00ter": "shooter",
    "f4ggots": "faggots",
    "b1tch": "bitch",
    "h4te": "hate",
    "l0ve": "love",
    "f4il": "fail",
    "s0": "so",
}

# Palabras de negación; se conservan aunque spaCy las considere stopwords.
NEGATION_WORDS: frozenset[str] = frozenset(
    {"no", "not", "never", "nobody", "nothing", "nowhere", "neither", "nor", "cannot"}
)


# --- Limpieza regex: solo caracteres, sin NLP ---
def _clean(text: str) -> str:
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


def _normalize_elongation(word: str) -> str:
    """sooooo -> so."""
    return re.sub(r"(.)\1{2,}", r"\1", word)


def _keep_token(token: Token) -> bool:
    """Las negaciones se conservan aunque sean stopwords de spaCy."""
    if token.text in NEGATION_WORDS:
        return True
    return (
        not (token.is_punct or token.is_stop or token.like_num)
        and len(token) > 2
        and len(set(token.text)) > 1
    )


def _mark_negation(tokens: Iterable[str]) -> list[str]:
    """not good -> not_good."""
    out: list[str] = []
    negated = False
    for word in tokens:
        if word in NEGATION_WORDS:
            negated = True
            continue
        out.append(("not_" if negated else "") + word)
        negated = False
    if negated:
        out.append("not")
    return out


class NormalizationService:
    """Limpia, filtra, lematiza y marca negaciones; los pipelines se cargan con load()."""

    def __init__(self) -> None:
        self._tokenizer: spacy.Language | None = None
        self._lemmatizer: spacy.Language | None = None
        self._loaded = False

    def load(self) -> None:
        """Idempotente; se llama desde el lifespan."""
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
        """RuntimeError si no hubo load()."""
        if not self.is_loaded:
            raise RuntimeError("NormalizationService not loaded")
        tokenizer = self._tokenizer
        lemmatizer = self._lemmatizer
        if tokenizer is None or lemmatizer is None:
            raise RuntimeError("NormalizationService not loaded")
        cleaned = _clean(text)
        tokens = [
            _normalize_elongation(token.text) for token in tokenizer(cleaned) if _keep_token(token)
        ]
        lemmas = [token.lemma_ for token in lemmatizer(" ".join(tokens))]
        return " ".join(_mark_negation(lemmas))


# Singleton inyectado por el router via Depends y cargado por el lifespan de main
normalization_service = NormalizationService()


def get_normalization_service() -> NormalizationService:
    return normalization_service
