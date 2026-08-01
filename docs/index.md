# Horus — Detección de Cyberbullying con ML

Proyecto de tesis de ingeniería informática: clasificación de texto para
detectar casos de cyberbullying usando machine learning.

## Descripción

El proyecto entrena modelos de clasificación binaria (bullying / no bullying)
sobre un dataset de textos y expone el mejor modelo a través de una aplicación
web con `Streamlit` (frontend) y `FastAPI` (backend).

## Repositorio

| Ruta | Descripción |
| ---- | ----------- |
| `data/` | Datos organizados en capas (crudo, intermedio, reporte) |
| `notebooks/` | Pipeline de investigación por fases con prefijos de nombre |
| `models/` | Modelos serializados (`.pkl`, versionados con Git LFS) |
| `conf/config.yaml` | Parámetros del pipeline |
| `src_fastapi/` | API de predicción (deploy) |
| `src_streamlit/` | Interfaz de usuario (deploy) |

## Pipeline de investigación

Las etapas se ejecutan en orden dentro de `notebooks/`:

1. **Preprocesamiento** (`00_clean_text_with_spacy.ipynb`) — limpieza y
   normalización del texto.
2. **EDA** (`01_explore_data.ipynb`) — análisis exploratorio de los datos.
3. **Features** (`02_build_tfidf_features.ipynb`) — vectorización TF-IDF.
4. **Modelado** (`03_train_compare_models.ipynb`) — entrenamiento, validación y
   exportación de los 9 clasificadores.

## Deploy

Para levantar la aplicación con Docker:

```sh
docker-compose up --build
```

- Streamlit: http://localhost:8501
- FastAPI (API y docs): http://localhost:8000

## Documentación

- Configuración del pipeline: `conf/config.yaml`
- Descripción de las capas de datos: `data/README.md`
- Detalle de las fases: `notebooks/README.md`
