import re
from typing import List

import spacy
from fastapi import FastAPI
from joblib import load
from pydantic import BaseModel
from unidecode import unidecode

nlp = spacy.load("en_core_web_sm")

base_url = "/api/v1"

app = FastAPI(
    title="Horus API",
    description="Horus API for bullying detection",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    root_path=base_url,
)


class Token(BaseModel):
    text: str
    lemma: str
    pos: str
    tag: str
    dep: str
    shape: str
    is_alpha: bool
    is_stop: bool


class Sentence(BaseModel):
    text: str
    tokens: List[Token]


class Text(BaseModel):
    text: str


class Entities(BaseModel):
    text: str
    entities: List[str]


class Prediction(BaseModel):
    label: str
    score: float


def normalize(text) -> str:
    URL_PATTERN = re.compile(
        r"""(?:https?:\/\/)?(?:www\.)?(?:[a-zA-Z0-9-]+\.[a-zA-Z]{2,6})(?:[-a-zA-Z0-9@:%_\+.~#?&\/\/=]*)""")
    MENTION_PATTERN = re.compile(r"@\S+")
    HASHTAG_PATTERN = re.compile(r"#\S+")
    RT_PATTERN = re.compile(r"RT")
    LETTERS_PATTERN = re.compile(r"[^a-zA-Z]")

    tokens = nlp(text)

    tokens = [token for token in tokens
              if not re.match(URL_PATTERN, token.text)
              and not re.match(MENTION_PATTERN, token.text)
              and not re.match(HASHTAG_PATTERN, token.text)
              and not re.match(RT_PATTERN, token.text)
              and not re.match(LETTERS_PATTERN, token.text)
              and not token.is_stop
              and not token.is_punct
              and not token.is_space
              and not token.is_digit
              and len(token.text) > 2]

    text = " ".join([unidecode(token.lemma_.strip().lower()) for token in tokens])

    return text


@app.post("/normalize")
async def normalize_text(text: Text) -> Text:
    text_normalized = normalize(text.text)
    return Text(text=text_normalized)


@app.post("/tokenize")
async def tokenize(text: Text) -> Sentence:
    doc = nlp(text.text)
    tokens = []
    for token in doc:
        tokens.append(Token(
            text=token.text,
            lemma=token.lemma_,
            pos=token.pos_,
            tag=token.tag_,
            dep=token.dep_,
            shape=token.shape_,
            is_alpha=token.is_alpha,
            is_stop=token.is_stop
        ))
    return Sentence(text=text.text, tokens=tokens)


@app.post("/entities")
async def entities(text: Text) -> Entities:
    doc = nlp(text.text)
    entities_list = [ent.text for ent in doc]
    return Entities(text=text.text, entities=entities_list)


@app.post("/predict")
async def predict(text: Text):
    # Normalizar texto
    text_normalized = normalize(text.text)
    # Vectorizar texto
    vectorizer = load("../models/tfidf_vectorizer.pkl")
    text_vectorized = vectorizer.transform([text_normalized])
    # Cargar modelo
    model = load("../models/polynomial_svm.pkl")
    # Predecir (Not_Bullying: 0, Bullying: 1)
    prediction = model.predict(text_vectorized)
    prediction = "Bullying" if prediction[0] == 1 else "Not Bullying"
    # Probabilidad
    probability = model.decision_function(text_vectorized)
    return Prediction(label=prediction, score=probability[0])


@app.get("/")
async def root() -> Text:
    return Text(text="Horus API is running!")
