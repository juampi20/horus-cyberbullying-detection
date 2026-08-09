# Nombres exactos de los paquetes de modelos .pkl que el pipeline espera.
# Los paths de los modelos NO viven acá: consultar core/config.py (MODELS_DIR,
# METRICS_PATH).
SUPPORTED_MODELS: tuple[str, ...] = (
    "gradient_boosting",
    "logistic_regression",
    "multinomial_naive_bayes",
    "neural_network",
    "random_forest",
    "support_vector_machine_(linear_kernel)",
    "xgboost",
)
