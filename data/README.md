# Datos

Carpeta de datos del pipeline. Los datos se organizan en capas según el estado
de procesamiento, siguiendo la convención del proyecto
`data-science-project-template`.

## Estructura

```
data/
├── raw/                 # Datos crudos, inmutables
├── processed/           # Datos preprocesados, listos para modelado
└── output/              # Resultados y artefactos de reporte
```

## Capas

### raw
Datos crudos tal como se obtienen de la fuente, sin ninguna transformación. No
se modifican ni se regeneran manualmente.

- `cyberbullying.csv` — dataset original de detección de cyberbullying
  (columnas: texto y etiqueta de clase).

### processed
Datos resultantes de transformaciones intermedias del pipeline. Son
deterministas a partir de la capa `raw` y el notebook `00_normalize`.

- `cyberbullying_preprocessed.csv` — texto normalizado y sin filas vacías,
  generado por `notebooks/00_normalize.ipynb`.

### output
Resultados de evaluación y métricas finales, generados por el notebook de
modelado. Alimentan la UI de deploy (Streamlit) vía API.

- `models_results.csv` — métricas (precisión, recall, F1, accuracy) de los 9
  modelos entrenados, exportadas por `notebooks/03_train.ipynb`.

Los modelos serializados (`.pkl`) viven en `models/`, fuera de esta carpeta.
