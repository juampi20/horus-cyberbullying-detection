import re

import spacy
from unidecode import unidecode

nlp = spacy.load("en_core_web_sm")


def normalize(text: str) -> str:
    text = text.lower()  # Convertir el texto a minúsculas
    text = re.sub(r"[^\x00-\x7F]+", "", text)  # Eliminar caracteres no ASCII
    text = re.sub(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", "", text)  # Eliminar emails
    text = re.sub(r"http\S+", "", text)  # Eliminar URLs
    text = re.sub(r"@\S+", "", text)  # Eliminar menciones
    text = re.sub(r"#\S+", "", text)  # Eliminar hashtags
    text = re.sub(r"RT", "", text)  # Eliminar RT
    text = re.sub(r"\s+", " ", text)  # Eliminar espacios en blanco
    text = re.sub(r"[^a-zA-Z]", " ", text)  # Eliminar caracteres que no sean letras
    text = ' '.join(unidecode(word) for word in text.split())
    text = ' '.join([word.text for word in nlp(text) if not (word.is_punct or word.is_stop or word.like_num)])
    text = ' '.join([word.text for word in nlp(text) if len(word) > 2])
    text = ' '.join([word.text for word in nlp(text) if len(set(word.text)) > 1])
    text = ' '.join([word.lemma_ for word in nlp(text)])
    return text
