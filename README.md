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
├── conf/             Parámetros del pipeline
├── .code_quality/    Configuración de ruff y mypy
├── Makefile          Calidad de código y pruebas
├── docker-compose.yml
└── install.sh
```

### backend

- `app/main.py` — bootstrap de la aplicación.
- `app/core/` — configuración por variables de entorno, constantes y logging.
- `app/api/` — endpoints, schemas y modelos serializados (`*.pkl`, Git LFS).
- `app/services/` — métricas y consenso entre modelos, normalización y
  traducción del texto.

### frontend

- `streamlit_app.py` — aplicación principal.
- `api.py` — cliente HTTP hacia la API.
- `consensus.py` — consenso entre modelos.
- `presentation.py` — componentes de presentación.
- `constants.py` — constantes de la UI.

## Investigación

Los notebooks corren en orden, cada fase consume lo que produce la anterior:

- `00_normalize` — carga el dataset crudo, normaliza el texto (minúsculas,
  limpieza de ruido, lematización con spaCy) y exporta el dataset preprocesado
  a `data/processed/`.
- `01_explore` — análisis exploratorio: distribución de clases, frecuencia de
  términos y estadísticas descriptivas.
- `02_features` — vectorización TF-IDF y features referenciales. La
  vectorización productiva ocurre dentro del pipeline de modelado.
- `03_train` — entrena los 7 clasificadores (pipeline `TfidfVectorizer` +
  clasificador), valida con CV (cv=5, F1), aplica el umbral de 0.5 y exporta
  los `.pkl` y métricas a `backend/app/api/models/`.

Los parámetros centrales del pipeline se documentan en `conf/config.yaml`.

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
docker-compose up --build
```

- Frontend (Streamlit): `http://localhost:8501`
- Backend (FastAPI): `http://localhost:8000` — la raíz redirige a la
  documentación interactiva del propio backend (Swagger UI).

## Uso de la Aplicación

1. Abre `http://localhost:8501`.
2. Ingresa el texto a clasificar.
3. Ejecuta y mira el veredicto del consenso ponderado por F1 y la comparación
   entre los 7 modelos.

- **Etiqueta**: veredicto del consenso: `Bullying`, `Not Bullying` o `Incierto`
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

El backend se configura por variables de entorno. Ver `.env.example` para la
lista completa con valores por defecto.

## Licencia

MIT — ver [`LICENSE`](LICENSE).
