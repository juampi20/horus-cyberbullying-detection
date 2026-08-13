# Detección de Cyberbullying en Texto

Aplicación web que clasifica textos como bullying o no bullying usando modelos de
aprendizaje automático. El frontend está construido con **Streamlit** y el backend
con **FastAPI**, exponiendo un endpoint de predicción con consenso entre múltiples
modelos.

## Arquitectura

```plaintext
.
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py              # Bootstrap de la aplicación FastAPI
│       ├── core/
│       │   ├── config.py        # Configuración por variables de entorno
│       │   ├── constants.py     # Constantes del dominio
│       │   └── logging.py       # Configuración de logging
│       ├── api/
│       │   ├── router.py        # Endpoints de la API
│       │   ├── schemas.py       # Schemas de request/response
│       │   └── models/          # Modelos serializados (*.pkl, Git LFS)
│       └── services/
│           ├── metrics.py       # Cálculo de métricas y consenso
│           ├── normalization.py # Normalización del texto
│           └── translation.py   # Traducción del texto (para modelos multilingües)
├── frontend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── streamlit_app.py         # Aplicación principal
│   ├── api.py                   # Cliente HTTP hacia la API
│   ├── consensus.py             # Lógica de consenso entre modelos
│   ├── presentation.py          # Componentes de presentación
│   └── constants.py             # Constantes de la UI
├── notebooks/
│   ├── 00_normalize.ipynb       # Normalización del dataset
│   ├── 01_explore.ipynb         # Análisis exploratorio
│   ├── 02_features.ipynb        # Ingeniería de features
│   └── 03_train.ipynb           # Entrenamiento y evaluación de modelos
├── data/
│   ├── README.md                # Documentación del dataset y fuentes
│   ├── processed/               # Datos preprocesados, versionados
│   └── raw/                     # NO versionado — descargar de Kaggle (ver data/README.md)
├── conf/
│   └── config.yaml              # Configuración de calidad de código
├── .code_quality/               # Configuración de ruff y mypy
├── Makefile                     # Comandos de calidad y pruebas
├── docker-compose.yml
└── install.sh
```

## Dataset

El dataset de entrenamiento proviene del corpus académico de detección de
cyberbullying de Wang, Fu y Lu (2020), distribuido públicamente en Kaggle:

- **Fuente académica**: J. Wang, K. Fu, C.T. Lu, "SOSNet: A Graph Convolutional
  Network Approach to Fine-Grained Cyberbullying Detection", Proceedings of the
  2020 IEEE International Conference on Big Data (IEEE BigData 2020).
- **Versión pública**: [andrewmvd/cyberbullying-classification](https://www.kaggle.com/datasets/andrewmvd/cyberbullying-classification)
  (licencia **CC BY 4.0**).

Los datos crudos (`data/raw/`) no se versionan en el repositorio: contienen
tweets reales con handles de terceros. Para reproducir el pipeline, descargar el
dataset de Kaggle y ubicarlo como `data/raw/cyberbullying.csv` (ver
[`data/README.md`](data/README.md)).

## Ejecución con Docker Compose

```sh
docker-compose up --build
```

- Frontend (Streamlit): `http://localhost:8501`
- Backend (FastAPI): `http://localhost:8000` — documentación interactiva en
  `http://localhost:8000/docs`

## Uso de la Aplicación

1. Abre `http://localhost:8501`.
2. Ingresa el texto a clasificar.
3. Selecciona el modelo (o usa el consenso entre modelos).
4. Ejecuta y observa la etiqueta predicha y la confianza.

### Interpretación de los Resultados

- **Etiqueta**: predicción del modelo: `Bullying` o `Not Bullying`.
- **Confianza**: grado de seguridad del modelo en su predicción, en porcentaje.

## Desarrollo local

```sh
# Calidad de código y pruebas del backend
make lint
make mypy
make test
```

## Configuración

El backend se configura mediante variables de entorno. Ver `.env.example` para
la lista completa con sus valores por defecto.

## Licencia

MIT — ver [`LICENSE`](LICENSE).
