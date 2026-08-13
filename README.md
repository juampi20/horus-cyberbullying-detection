# Horus — Detección de Cyberbullying con ML

Proyecto de tesis de ingeniería informática. Clasifica texto como bullying o no
bullying con machine learning, entrena 7 modelos, combina sus predicciones en un
consenso ponderado por F1 y muestra el resultado en una aplicación web.

Toda la investigación (análisis exploratorio, features, entrenamiento,
evaluación) está en los notebooks de [`notebooks/`](notebooks/), ejecutables en
orden. El deploy es solo la cara visible del pipeline.

## Estructura

```plaintext
.
├── backend/          API de predicción (FastAPI)
├── frontend/         Aplicación web (Streamlit)
├── notebooks/        Pipeline de investigación
├── data/             Datos del pipeline
├── .code_quality/    Configuración de ruff y mypy
├── Makefile          Calidad de código, pruebas y deploy
└── docker-compose.yml
```

### backend

- `app/main.py`: bootstrap de la aplicación.
- `app/core/`: configuración por variables de entorno, constantes y logging.
- `app/api/`: endpoints, schemas y modelos serializados (`*.pkl`, Git LFS).
- `app/services/`: métricas y consenso entre modelos, normalización y
  traducción del texto.

### frontend

- `streamlit_app.py`: aplicación principal.
- `api.py`: cliente HTTP hacia la API.
- `consensus.py`: consenso entre modelos.
- `presentation.py`: componentes de presentación.
- `constants.py`: constantes de la UI.

## Investigación

Los notebooks corren en orden, cada fase consume lo que produce la anterior:

- `00_normalize`: carga el dataset crudo, normaliza el texto (minúsculas,
  limpieza de ruido, lematización con spaCy) y exporta el dataset preprocesado
  a `data/processed/`.
- `01_explore`: análisis exploratorio. Distribución de clases, frecuencia de
  términos y estadísticas descriptivas.
- `02_features`: vectorización TF-IDF y features referenciales. La
  vectorización productiva ocurre dentro del pipeline de modelado.
- `03_train`: entrena los 7 clasificadores (pipeline `TfidfVectorizer` +
  clasificador), valida con CV (cv=5, F1), aplica el umbral de 0.5 y exporta
  los `.pkl` y métricas a `backend/app/api/models/`.

Los parámetros del pipeline (CV=5, umbral 0.5, F1, modelos) están detallados en
`docs/mvp_scope_and_limitations.md`.

## Dataset

El dataset viene del corpus académico de detección de cyberbullying de Wang,
Fu y Lu (2020), distribuido públicamente en Kaggle:

- **Fuente académica**: J. Wang, K. Fu, C.T. Lu, "SOSNet: A Graph Convolutional
  Network Approach to Fine-Grained Cyberbullying Detection", Proceedings of the
  2020 IEEE International Conference on Big Data (IEEE BigData 2020).
- **Versión pública**: [andrewmvd/cyberbullying-classification](https://www.kaggle.com/datasets/andrewmvd/cyberbullying-classification)
  (licencia **CC BY 4.0**).

Los datos crudos (`data/raw/`) no se versionan: contienen tweets reales con
handles de terceros. Para reproducir el pipeline, descargar el dataset de
Kaggle y ubicarlo como `data/raw/cyberbullying.csv` (81.417 filas, columnas
`tweet_text` y `cyberbullying_type` binaria 0/1).

## Ejecución con Docker Compose

```sh
make up
```

- Frontend (Streamlit): `http://localhost:8501`
- Backend (FastAPI): `http://localhost:8000`. La raíz redirige a la
  documentación interactiva del propio backend (Swagger UI).

Comandos útiles: `make down` (detener), `make logs` (logs en vivo), `make ps`
(estado).

## Uso de la Aplicación

1. Abre `http://localhost:8501`.
2. Ingresa el texto a clasificar.
3. Ejecuta y mira el veredicto del consenso ponderado por F1 y la comparación
   entre los 7 modelos.

- **Etiqueta**: veredicto del consenso: `Bullying`, `No Bullying` o `Incierto`
  (banda de incertidumbre 45–55%).
- **Confianza**: score ponderado de bullying y acuerdo entre modelos, en
  porcentaje.

## Desarrollo local

```sh
make lint
make mypy
make test
```

## Configuración

El backend y el frontend se configuran por variables de entorno. Todas tienen
valores por defecto, así que el proyecto corre sin configuración adicional.

| Variable | Default | Descripción |
| -------- | ------- | ----------- |
| `API_URL` | `http://localhost:8000/` | URL del backend que usa el frontend (la define docker-compose) |
| `MODELS_DIR` | `backend/app/api/models` | Carpeta de los modelos serializados |
| `METRICS_PATH` | `backend/app/api/models/models_results.csv` | Archivo de métricas |
| `CORS_ORIGINS` | `["*"]` | Orígenes permitidos en el backend |
| `LOG_LEVEL` | `INFO` | Nivel de logging |
| `MODEL_TIMEOUT_SECONDS` | `10.0` | Timeout por predicción en segundos |

## Documentación

- `docs/mvp_scope_and_limitations.md`: alcance del MVP, justificación y
  limitaciones (respaldo para la tesis).

## Licencia

MIT. Ver [`LICENSE`](LICENSE).
