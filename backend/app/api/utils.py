import re

import spacy
from unidecode import unidecode

nlp = spacy.load("en_core_web_sm")


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\x00-\x7F]+", "", text)
    text = re.sub(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", "", text)
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"@\S+", "", text)
    text = re.sub(r"#\S+", "", text)
    text = re.sub(r"RT", "", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^a-zA-Z]", " ", text)
    text = " ".join(unidecode(word) for word in text.split())

    # Una sola pasada de spaCy: filtro stopwords/punt/números, longitud>2, dedupe de chars
    # (len(set)>1) y lematización en la misma iteración (equivale a las 4 pasadas previas).
    doc = nlp(text)
    return " ".join(
        token.lemma_
        for token in doc
        if not (token.is_punct or token.is_stop or token.like_num)
        and len(token.text) > 2
        and len(set(token.text)) > 1
    )
