# Notebooks

Notebooks del pipeline de investigación, organizados por fase según la
convención del proyecto `data-science-project-template`. Se ejecutan en orden
y cada fase consume el artefacto que produce la anterior.

## Fases

```
notebooks/
├── 1-data/               # Obtención y preprocesamiento de datos
├── 2-exploration/        # Análisis exploratorio (EDA)
├── 4-feat_eng/           # Ingeniería de features
└── 5-models/             # Modelado, evaluación y exportación
```

### 1-data
- `00_preprocessing.ipynb` — carga el dataset crudo, normaliza el texto
  (minúsculas, limpieza de ruido, lematización con spaCy) y exporta el dataset
  preprocesado a `data/02_intermediate/`.

### 2-exploration
- `02_eda.ipynb` — análisis exploratorio sobre el dataset preprocesado:
  distribución de clases, frecuencia de términos y estadísticas descriptivas.

### 4-feat_eng
- `01_features.ipynb` — vectorización TF-IDF y construcción de features
  referenciales para el análisis exploratorio. La vectorización productiva
  ocurre dentro del pipeline de modelado.

### 5-models
- `03_modeling.ipynb` — entrena los 9 clasificadores (pipeline
  `TfidfVectorizer + clasificador`), valida con CV (cv=5, F1), aplica el umbral
  de decisión de 0.5 y exporta los `.pkl` a `models/` y las métricas a
  `data/08_reporting/models_results.csv`.

## Convenciones

- Las rutas de datos se escriben de forma relativa a cada notebook
  (`../../data/...`, `../../models/...`).
- Los parámetros centrales del pipeline se documentan en `conf/config.yaml`.
