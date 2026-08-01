# Datos

Carpeta de datos del pipeline. Los datos se organizan en capas según el estado
de procesamiento, siguiendo la convención del proyecto
`data-science-project-template`.

## Estructura

```
data/
├── 01_raw/              # Datos crudos, inmutables
├── 02_intermediate/     # Datos preprocesados, listos para modelado
└── 08_reporting/        # Resultados y artefactos de reporte
```

## Capas

### 01_raw
Datos crudos tal como se obtienen de la fuente, sin ninguna transformación. No
se modifican ni se regeneran manualmente.

- `cyberbullying.csv` — dataset original de detección de cyberbullying
  (columnas: texto y etiqueta de clase).

### 02_intermediate
Datos resultantes de transformaciones intermedias del pipeline. Son
deterministas a partir de la capa `01_raw` y el notebook `00_preprocessing`.

- `cyberbullying_preprocessed.csv` — texto normalizado y sin filas vacías,
  generado por `notebooks/1-data_00_preprocessing.ipynb`.

### 08_reporting
Resultados de evaluación y métricas finales, generados por el notebook de
modelado. Alimentan la UI de deploy (Streamlit) vía API.

- `models_results.csv` — métricas (precisión, recall, F1, accuracy) de los 9
  modelos entrenados, exportadas por `notebooks/5-models_03_modeling.ipynb`.

Los modelos serializados (`.pkl`) viven en `models/`, fuera de esta carpeta.
