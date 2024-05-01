from flask import request, jsonify, Response
from flask.views import MethodView

from src.utils.helpers import clean_text
from .models import CyberbullyingDetectionModel


class PredictView(MethodView):
    def post(self) -> Response:
        """
        Maneja las solicitudes POST al endpoint de predicción.

        El cuerpo de la solicitud debe contener un objeto JSON con una clave 'text' que contenga el texto a analizar.

        Devuelve:
            Una respuesta JSON que contiene el resultado de la predicción si la solicitud es exitosa.
            Si la clave 'text' no se proporciona en el cuerpo de la solicitud, devuelve una respuesta JSON con un mensaje de error.
        """
        text = request.json.get('text')
        if not text or text.strip() == '':
            return jsonify({'error': 'No se proporcionó un texto válido'}), 400
        text = clean_text(text)
        model = CyberbullyingDetectionModel()
        prediction = model.predict(text)
        return jsonify({'prediction': prediction})
