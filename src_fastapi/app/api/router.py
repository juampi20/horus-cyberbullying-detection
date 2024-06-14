import os
from typing import Any

from deep_translator import GoogleTranslator
from fastapi import APIRouter
from joblib import load

from .constants import MODELS_PATH
from .schemas import Input, ClassResponse
from .utils import normalize

classification_router = APIRouter()


# Get Models Info
@classification_router.get("/info")
async def get_models_info():
    models_info_path = os.path.join(MODELS_PATH, "models_results.csv")
    models_info: dict[str: dict[str, Any]] = {}
    with open(models_info_path, "r") as f:
        for line in f.readlines()[1:]:
            model, precision, recall, f1, accuracy = line.strip().split(",")
            models_info[model] = {
                "precision": float(precision),
                "f1": float(f1),
                "recall": float(recall),
                "accuracy": float(accuracy)
            }
    return models_info


@classification_router.post("/predict", response_model=ClassResponse)
async def classify(item: Input) -> dict[str, str | Any]:
    text_translated = GoogleTranslator(source="auto", target="en").translate(item.text)
    print("Texto traducido: ", text_translated)
    text_normalized = normalize(str(text_translated))
    model_type = item.model.lower().replace(" ", "_")
    model = load(os.path.join(MODELS_PATH, f"{model_type}.pkl"))
    prediction = model.predict([text_normalized])
    prediction = "Bullying" if prediction[0] == 1 else "Not Bullying"
    probability = model.predict_proba([text_normalized])
    return {
        "category": prediction,
        "confidence": round(probability[0][1], 2)
    }
