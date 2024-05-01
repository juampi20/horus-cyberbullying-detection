import joblib


class CyberbullyingDetectionModel:
    def __init__(self):
        self.classifier = joblib.load('../models/polynomial_svm.pkl')
        self.vectorizer = joblib.load('../models/tfidf_vectorizer.pkl')

    def predict(self, text) -> bool:
        features = self.vectorizer.transform([text])
        prediction = self.classifier.predict(features)[0]
        return bool(prediction)
