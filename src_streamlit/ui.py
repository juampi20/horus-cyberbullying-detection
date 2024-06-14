import json
import os
from collections import namedtuple

import pandas as pd
import requests
import streamlit as st


def color_bg(category):
    Color = namedtuple("Color", ["bg"])
    formatting = {
        "Bullying": Color(bg="#FF6347"),
        "Not Bullying": Color(bg="#90EE90"),
    }
    colors = formatting.get(category, None)
    if colors:
        return f"""<mark style="background-color: {colors.bg};">{category}</mark>"""
    return category


class ApiCalls:
    def __init__(self, url: str = os.getenv("API_URL", default="http://localhost:8000/")) -> None:
        self.url = url
        self.headers = {"Content-Type": "application/json"}

    def healthcheck(self, retries: int = 3) -> bool:
        endpoint = self.url + "healthcheck"
        for _ in range(retries):
            try:
                response = requests.get(url=endpoint)
                if response.status_code == 200:
                    return True
            except requests.exceptions.ConnectionError:
                pass
        return False

    def model_list(self) -> dict:
        endpoint = self.url + "api/v1/classification/info"
        models = requests.get(url=endpoint)

        if models.text:
            try:
                return json.loads(models.text)
            except json.JSONDecodeError:
                print("Error: Response is not a valid JSON document")
                return {}
        else:
            print("Error: Response is empty")
            return {}

    def make_predict(self, model: str, text: str) -> json:
        endpoint = self.url + "api/v1/classification/predict"

        payload = {"model": model.lower(), "text": text}
        result = requests.post(
            url=endpoint, headers=self.headers, data=json.dumps(payload)
        )
        return json.loads(result.text)


def main():
    st.set_page_config(
        page_title="Horus",
        page_icon="🧙‍♂️",
        layout="centered"
    )

    st.title("🧙‍♂️ Horus")
    st.write("Horus es un modelo de clasificación de texto que identifica si un texto es un caso de bullying o no.")

    apicall = ApiCalls()

    with st.spinner(text="Esperando respuesta del servidor..."):
        is_alive = apicall.healthcheck()

    if not is_alive:
        st.error("Error: No se pudo conectar con el servidor de Horus")
        st.stop()

    models_dict: dict = apicall.model_list()
    models_df = pd.DataFrame(models_dict).T
    models_df = models_df.sort_values(by="f1", ascending=False)
    model_names = models_df.index.tolist()

    with st.expander("📊 Modelos Entrenados"):
        st.markdown("""
        Los modelos entrenados son clasificadores binarios que predicen si un texto es un caso de bullying o no. 
        
        Se entrenaron con diferentes algoritmos y se evaluaron con las métricas de precisión, recall, f1 y accuracy.
        """)
        st.dataframe(models_df, use_container_width=True)
        st.write(
            "Para entender más sobre estas métricas, ver [aquí](https://developers.google.com/machine-learning/crash-course/classification/precision-and-recall?hl=es-419)")

    with st.expander("🔎 Interpretación de los Resultados"):
        st.markdown("""
        Se obtienen dos valores en la predicción:
        
        - **Etiqueta**: Es la predicción del modelo. Puede ser "Bullying" o "Not Bullying".
        - **Confianza**: Verifica el grado de detección de Bullying en el texto, según el modelo.

        El modelo utiliza un umbral de 50% para determinar la etiqueta. Si la confianza es mayor o igual al 50%, el modelo predice "Bullying". Si es menor al 50%, predice "Not Bullying".
        """)

    "### 📝 Clasificación de Texto"

    # Recommended model: Neural Network
    recommended_model = "Neural Network"
    recommended_model_index = model_names.index(recommended_model)
    model_names[recommended_model_index] = f"{recommended_model} ❤️"

    with st.form("Clasificacion de Texto"):
        model: str = st.selectbox("Seleccionar modelo entrenado:", model_names, index=recommended_model_index)
        input_text: str = st.text_area("Ingresar texto a clasificar:")
        run_button: bool = st.form_submit_button("Ejecutar")

    if run_button:
        with st.spinner(text="Obteniendo resultados..."):
            if input_text.strip() == "":
                st.error("Error: El texto ingresado está vacío.")
                st.stop()
            try:
                if "❤️" in model:
                    model = model.replace(" ❤️", "")
                result = apicall.make_predict(
                    model=model.lower(),
                    text=input_text,
                )
            except Exception as e:
                st.error(f"Error: {e}")
                st.stop()

        if not result:
            st.error("Error: No se obtuvo respuesta del servidor")
            st.stop()

        # Mostrar resultados
        "### 📗 Resultado:"
        st.markdown(
            f"El texto fue etiquetado como **{color_bg(result['category'])}** con una confianza de **{result['confidence'] * 100:.2f}%**.",
            unsafe_allow_html=True
        )


if __name__ == "__main__":
    main()
    # CLI: streamlit run ./src_streamlit/ui.py
