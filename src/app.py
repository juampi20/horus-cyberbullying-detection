from flask import Flask

from api.views import PredictView


def create_app():
    app = Flask(__name__)

    @app.route('/')
    def home():
        return "API is working correctly"

    # Registrar las vistas
    app.add_url_rule('/predict', view_func=PredictView.as_view('predict'))

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
