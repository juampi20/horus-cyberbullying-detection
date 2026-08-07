from pathlib import Path

# Path del repo root (backend/app/api/constants.py -> parents[3] = <repo-root>)
REPO_ROOT = Path(__file__).resolve().parents[3]

# Paquetes de modelos .pkl que el pipeline espera en la raíz del repo
SUPPORTED_MODELS: tuple[str, ...] = (
    "gradient_boosting",
    "logistic_regression",
    "multinomial_naive_bayes",
    "neural_network",
    "random_forest",
    "support_vector_machine_(linear_kernel)",
    "xgboost",
)

# Ruta de los modelos .pkl (formato joblib) en la raíz del repo
MODELS_PATH = REPO_ROOT / "models"

# Ruta del CSV de métricas (NO está en models/, vive dentro de backend/app/api/models).
# Es relativa al código: así resuelve igual en host (backend/app/api/models) y en el
# container (el COPY . /app/ deja el CSV en /app/app/api/models).
METRICS_PATH = Path(__file__).resolve().parent / "models" / "models_results.csv"
