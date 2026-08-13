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

La carpeta `raw/` **no se versiona en el repositorio** (ver `.gitignore`): contiene
tweets reales con handles de terceros y el dataset redistribuido es una versión
binarizada que no coincide exactamente con el original de Kaggle. Para
reproducir el pipeline, descargar el dataset y ubicarlo como
`data/raw/cyberbullying.csv`:

- Fuente académica: J. Wang, K. Fu, C.T. Lu, "SOSNet: A Graph Convolutional
  Network Approach to Fine-Grained Cyberbullying Detection", Proceedings of the
  2020 IEEE International Conference on Big Data (IEEE BigData 2020).
- Versión pública: `andrewmvd/cyberbullying-classification` en Kaggle
  (licencia CC BY 4.0) — https://www.kaggle.com/datasets/andrewmvd/cyberbullying-classification

- `cyberbullying.csv` — dataset de detección de cyberbullying (81.417 filas,
  columnas `tweet_text` y `cyberbullying_type` binaria 0/1).

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
