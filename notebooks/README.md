# Notebooks

Notebooks del pipeline de investigación, organizados por fase según la
convención del proyecto `data-science-project-template`. Se ejecutan en orden
y cada fase consume el artefacto que produce la anterior.

## Fases

```
notebooks/
├── 00_clean_text_with_spacy.ipynb     # Obtención y preprocesamiento de datos
├── 01_explore_data.ipynb              # Análisis exploratorio (EDA)
├── 02_build_tfidf_features.ipynb      # Ingeniería de features
└── 03_train_compare_models.ipynb      # Modelado, evaluación y exportación
```

### 00_clean_text_with_spacy.ipynb
- Carga el dataset crudo, normaliza el texto (minúsculas, limpieza de ruido,
  lematización con spaCy) y exporta el dataset preprocesado a
  `data/02_intermediate/`.

### 01_explore_data.ipynb
- Análisis exploratorio sobre el dataset preprocesado: distribución de clases,
  frecuencia de términos y estadísticas descriptivas.

### 02_build_tfidf_features.ipynb
- Vectorización TF-IDF y construcción de features referenciales para el análisis
  exploratorio. La vectorización productiva ocurre dentro del pipeline de
  modelado.

### 03_train_compare_models.ipynb
- Entrena los 9 clasificadores (pipeline `TfidfVectorizer + clasificador`),
  valida con CV (cv=5, F1), aplica el umbral de decisión de 0.5 y exporta los
  `.pkl` a `models/` y las métricas a `data/08_reporting/models_results.csv`.

## Convenciones

- Las rutas de datos se escriben de forma relativa a cada notebook
  (`../data/...`, `../models/...`).
- Los parámetros centrales del pipeline se documentan en `conf/config.yaml`.
