# Proyecto de Clasificación de Texto para Detección de Bullying

Este proyecto consiste en una aplicación web que utiliza modelos de clasificación de texto para identificar si un texto
es un caso de bullying o no. La aplicación está construida con `Streamlit` para la interfaz de usuario y `FastAPI` para
el backend.

## Arquitectura del Proyecto

### Estructura del Frontend & Backend

```plaintext
.
├── src_fastapi/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── models/
│   │   └── models_results.csv
│   └── app/
│       ├── main.py
│       └── api/
│           ├── config.py
│           ├── constants.py
│           ├── router.py
│           ├── schemas.py
│           └── utils.py
├── src_streamlit/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── ui.py
├── docker-compose.yml
└── README.md
```

### Servicios

- **FastAPI**: Servicio backend que maneja las solicitudes de predicción y proporciona la API para la clasificación de
  texto.
- **Streamlit**: Servicio frontend que proporciona la interfaz de usuario para interactuar con el modelo de
  clasificación.

### Configuración de Docker Compose

El archivo `docker-compose.yml` define dos servicios: `fastapi` y `streamlit`.

```yaml
version: '3.7'

services:
  fastapi:
    container_name: fastapi
    build: ./src_fastapi
    ports:
      - "8000:8000"
    networks:
      - deploy_network

  streamlit:
    container_name: streamlit
    build: ./src_streamlit
    depends_on:
      - fastapi
    ports:
      - "8501:8501"
    networks:
      - deploy_network
    environment:
      - API_URL=http://fastapi:8000/

networks:
  deploy_network:
    driver: bridge
```

### Dependencias

#### Backend (`src_fastapi/requirements.txt`)

```text
fastapi==0.70.0
uvicorn==0.15.0
spacy==3.2.0
```

#### Frontend (`src_streamlit/requirements.txt`)

```text
streamlit==1.35.0
streamlit-extras==0.4.3
requests==2.32.2
```

### Ejecución del Proyecto

Para ejecutar el proyecto, asegúrate de tener Docker y Docker Compose instalados. Luego, ejecuta el siguiente comando en
la raíz del proyecto:

```sh
docker-compose up --build
```

Esto construirá y levantará los servicios `fastapi` y `streamlit`. La aplicación `Streamlit` estará disponible
en `http://localhost:8501` y el backend `FastAPI` en `http://localhost:8000`.

### Uso de la Aplicación

1. Abre tu navegador y ve a `http://localhost:8501`.
2. Ingresa el texto que deseas clasificar en el área de texto proporcionada.
3. Selecciona el modelo entrenado que deseas usar para la clasificación.
4. Haz clic en el botón "Ejecutar" para obtener los resultados.

### Interpretación de los Resultados

- **Etiqueta**: Es la predicción del modelo. Puede ser "Bullying" o "Not Bullying".
- **Confianza**: Es el grado de seguridad que tiene el modelo en su predicción, expresado en porcentaje. Por ejemplo,
  una confianza de 80% significa que el modelo estima que hay un 80% de probabilidad de que su predicción sea correcta.

El modelo utiliza un umbral de 50% para determinar la etiqueta. Si la confianza es mayor al 50%, el modelo predice "
Bullying". Si es menor al 50%, predice "Not Bullying".
