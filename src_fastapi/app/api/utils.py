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
    text = ' '.join(unidecode(word) for word in text.split())
    text = ' '.join([word.text for word in nlp(text) if not (word.is_punct or word.is_stop or word.like_num)])
    text = ' '.join([word.text for word in nlp(text) if len(word) > 2])
    text = ' '.join([word.text for word in nlp(text) if len(set(word.text)) > 1])
    text = ' '.join([word.lemma_ for word in nlp(text)])
    return text
