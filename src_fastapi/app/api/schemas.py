from pydantic import BaseModel


# Model for recieveing input
class Input(BaseModel):
    model: str
    text: str


# Model for classification service response
class ClassResponse(BaseModel):
    category: str
    confidence: float
