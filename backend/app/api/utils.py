"""Normalización de texto previa al modelado.

Replica EXACTA del pipeline definido en notebooks/00_normalize.ipynb (celda de
normalización): minúsculas -> html.unescape -> contracciones/slang/leetspeak ->
regex (no-ASCII, emails, URLs, menciones, hashtags, RT, no-letras) -> unidecode
-> elongación -> filtro léxico (tokenizer mínimo) -> lematización (lemmatizer
completo) -> marcado de negación.

El orden no es arbitrario: la expansión de contracciones ocurre antes de la
limpieza regex para que el `not` de "doesn't" sobreviva y dispare el marcado de
negación, y la negación se marca sobre los lemas (no antes) para no romper la
lematización.
"""

import html
import re
from collections.abc import Iterable

import spacy
from spacy.tokens import Token
from unidecode import unidecode

# Dos pipelines del mismo modelo, decisión de rendimiento del notebook: el
# filtrado léxico no necesita tagger/parser (tokenizer mínimo, ~8x más rápido)
# y la lematización sí los usa (lemmatizer completo, disable=["ner"]).
lemmatizer = spacy.load("en_core_web_sm", disable=["ner"])
tokenizer = spacy.load(
    "en_core_web_sm",
    disable=["tagger", "parser", "ner", "attribute_ruler", "lemmatizer"],
)


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
    # Contracciones coloquiales
    "gonna": "going to",
    "wanna": "want to",
    "gotta": "got to",
    "lemme": "let me",
    "gimme": "give me",
    "imma": "i am going to",
    "kinda": "kind of",
    "sorta": "sort of",
    "dunno": "do not know",
    # Abreviaturas de opinión (alimentan la negación: idk -> i do not know)
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
    # Chatspeak fonético: variantes escritas como suenan
    "aint": "are not",  # alimenta la negación: aint funny -> not_funny
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

# Leetspeak real del dataset (b4 = before, h8 = hate)
LEET = {
    # Frecuentes en este dataset (medido sobre 81k textos)
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
    # Insultos ofuscados (críticos para cyberbullying)
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

# Palabras de negación que disparan el marking (not_good); se conservan aunque
# spaCy las considere stopwords.
NEGATION_WORDS: frozenset[str] = frozenset(
    {"no", "not", "never", "nobody", "nothing", "nowhere", "neither", "nor", "cannot"}
)


# --- Limpieza regex: solo caracteres, sin NLP ---
def clean(text: str) -> str:
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
    """Contrae la elongación: sooooo -> so, noooo -> no."""
    return re.sub(r"(.)\1{2,}", r"\1", word)


def keep_token(token: Token) -> bool:
    """Mantiene un token si es útil. Las negaciones se conservan SIEMPRE,
    aunque sean stopwords (not, no, never...)."""
    if token.text in NEGATION_WORDS:
        return True
    return (
        not (token.is_punct or token.is_stop or token.like_num)
        and len(token) > 2
        and len(set(token.text)) > 1
    )


def mark_negation(tokens: Iterable[str]) -> list[str]:
    """Prefija not_ al token siguiente a una negación. not good -> not_good."""
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


def normalize(text: str) -> str:
    """Limpia, filtra, lematiza y marca negaciones (paridad con el notebook 00)."""
    cleaned = clean(text)
    tokens = [normalize_elongation(token.text) for token in tokenizer(cleaned) if keep_token(token)]
    lemmas = [token.lemma_ for token in lemmatizer(" ".join(tokens))]
    return " ".join(mark_negation(lemmas))
