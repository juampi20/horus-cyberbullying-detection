# horus-cyberbullying-detection
El proyecto "Horus" es una solución de detección de ciberacoso que utiliza técnicas de procesamiento de lenguaje natural y aprendizaje automático.

La estructura del proyecto es la siguiente:

- `/src`: Este directorio contiene el código fuente de tu aplicación Flask.
    - `/api`: Este directorio contiene el código de tu API.
        - `__init__.py`: Este archivo se utiliza para indicar a Python que este directorio debe ser tratado como un
          paquete.
        - `views.py`: Este archivo contiene las vistas de tu API, que definen cómo se manejan las solicitudes.
        - `models.py`: Este archivo contiene los modelos de tu aplicación, que definen la estructura de tus datos.
    - `/utils`: Este directorio contiene cualquier código de utilidad que necesites.
        - `__init__.py`: Este archivo se utiliza para indicar a Python que este directorio debe ser tratado como un
          paquete.
        - `helpers.py`: Este archivo puede contener funciones de ayuda que necesites en tu aplicación.
    - `app.py`: Este es el archivo principal de tu aplicación Flask. Aquí es donde inicializas tu aplicación y registras
      tus vistas.
- `/models`: Este directorio contiene tu modelo de aprendizaje automático y tu vectorizador.
- `/data`: Este directorio contiene los datos con los que entrenaste tu modelo.
- `/notebooks`: Este directorio contiene tus notebooks de Jupyter.
- `.gitignore`: Este archivo le dice a Git qué archivos o directorios ignorar.
- `README.md`: Este archivo contiene información sobre tu proyecto.
- `requirements.txt`: Este archivo lista las dependencias de Python que tu proyecto necesita.
