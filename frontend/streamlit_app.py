"""Entry point de la UI de Streamlit para Horus."""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st
from api import ApiCalls, fetch_models
from consensus import (
    classify_consensus,
    compute_weighted_consensus,
    f1_weights,
)
from constants import (
    EXAMPLES,
    UNCERTAINTY_MARGIN,
    WEIGHT_AMPLIFICATION,
)
from presentation import (
    color_bg,
    decision_rule_cards,
    display_category,
    is_short_text,
    metric_card,
)


def to_snake_case(name: str) -> str:
    """Convierte un nombre para mostrar (ej. Random Forest) a snake_case."""
    return name.lower().replace(" ", "_")


def render_classification_input() -> tuple[str, bool]:
    """Renderiza el titulo, el boton de ejemplo y el form de clasificacion."""
    st.markdown("### Clasificacion de Texto")

    btn_cols = st.columns(2)
    with btn_cols[0]:
        if st.button("Probar con un ejemplo"):
            example_idx = st.session_state["example_index"]
            st.session_state["text_input"] = EXAMPLES[example_idx]
            st.session_state["example_index"] = (example_idx + 1) % len(EXAMPLES)

    with st.form("Clasificacion de Texto"):
        input_text: str = st.text_area("Ingresar texto a clasificar:", key="text_input")
        run_button: bool = st.form_submit_button("Ejecutar")
    return input_text, run_button


def render_classification_results(snapshot: dict[str, Any], models_df: pd.DataFrame) -> None:
    """Renderiza el veredicto, las tarjetas, el progreso, las advertencias y la tabla."""
    results = snapshot["results"]
    display_name_by_snake = snapshot["name_lookup"]
    weighted_score = snapshot["weighted_score"]
    agreement_pct = snapshot["agreement_pct"]

    failed_display_names = snapshot.get("failed_display_names") or []
    if failed_display_names:
        st.warning(
            "Algunos modelos fallaron y no participaron del consenso: "
            + ", ".join(failed_display_names)
            + "."
        )

    verdict = classify_consensus(weighted_score, margin=UNCERTAINTY_MARGIN)

    st.markdown(
        f"Resultado del consenso entre todos los modelos: "
        f"**{color_bg(display_category(verdict))}**",
        unsafe_allow_html=True,
    )

    prob_col, agree_col = st.columns(2)
    prob_col.markdown(
        metric_card("Probabilidad de bullying", f"{weighted_score * 100:.1f}%"),
        unsafe_allow_html=True,
    )
    agree_col.markdown(
        metric_card("Acuerdo entre modelos", f"{agreement_pct:.1f}%"),
        unsafe_allow_html=True,
    )
    st.progress(weighted_score, text="Probabilidad de bullying sobre el total ponderado")
    st.caption("Consenso ponderado por F1: los modelos con mejor F1 pesan mas en el voto.")

    st.markdown("#### Regla de decision")
    card_cols = st.columns(3)
    for col, card in zip(card_cols, decision_rule_cards()):
        col.markdown(
            f'<div style="border:1px solid rgba(255,255,255,0.15);'
            f" border-radius:8px; padding:10px; text-align:center;"
            f' background:rgba(255,255,255,0.04);">'
            f'<div style="font-size:0.85rem; opacity:0.7; margin-bottom:4px;">'
            f"{card['range']}</div>{color_bg(card['label'])}</div>",
            unsafe_allow_html=True,
        )

    if is_short_text(snapshot["input_text"]):
        st.markdown('<div style="height:16px;"></div>', unsafe_allow_html=True)
        st.warning("El texto es muy corto. La clasificacion puede ser poco confiable.")
    if verdict == "Uncertain":
        st.markdown('<div style="height:16px;"></div>', unsafe_allow_html=True)
        st.warning(
            f"Resultado incierto: los modelos estan divididos (acuerdo "
            f"{agreement_pct:.1f}%). Proba con un texto mas largo o mas claro."
        )

    f1_by_model: dict[str, float] = {
        to_snake_case(name): float(f1) for name, f1 in models_df["f1"].items()
    }

    compare_rows: list[dict[str, Any]] = []
    for result in results:
        display_name = display_name_by_snake.get(result["model"], result["model"])
        row_dict: dict[str, Any] = {
            "Modelo": display_name,
            "Categoria": display_category(result["category"]),
            "Confianza": result["confidence"] * 100,
            "Tiempo (ms)": result["inference_time_ms"],
        }
        compare_rows.append(row_dict)

    compare_rows.sort(
        key=lambda row: f1_by_model.get(to_snake_case(row["Modelo"]), 0), reverse=True
    )
    compare_df = pd.DataFrame(compare_rows)
    st.markdown("#### Comparacion entre todos los modelos")
    st.dataframe(
        compare_df,
        use_container_width=True,
        column_config={
            "Confianza": st.column_config.ProgressColumn(
                "Confianza", min_value=0, max_value=100, format="%.1f%%"
            ),
            "Tiempo (ms)": st.column_config.NumberColumn("Tiempo", format="%.1f ms"),
        },
    )


def render_guide(models_df: pd.DataFrame) -> None:
    """Renderiza el expander de la guia "¿Como funciona Horus?"."""
    with st.expander("¿Como funciona Horus?"):
        # 1. Consenso Ponderado por F1
        st.header("Consenso Ponderado por F1")
        st.markdown(
            "Horus combina las predicciones de 7 modelos asignando mayor peso "
            "a aquellos con mejor F1-score en la decision final."
        )

        st.code(
            "position = (F1 - F1_min) / (F1_max - F1_min)\n"
            f"weight = 1.0 + position × ({WEIGHT_AMPLIFICATION} - 1.0)\n"
            "score = Σ(weight_i × is_bullying_i) / Σ(weight_i)",
            language="python",
        )

        # 2. Interpretacion de Resultados: Etiqueta y Confianza
        st.header("Interpretacion de Resultados")
        st.markdown(
            "- **Etiqueta:** Prediccion individual de cada modelo (`Bullying` o `No Bullying`).\n"
            "- **Confianza:** Grado de certeza (0% - 100%) que asigna el modelo a su etiqueta."
        )

        # 3. Regla de Decision
        st.header("Regla de Decision")
        st.markdown(
            "El score de consenso se evalua frente a una banda de incertidumbre "
            "(±5% alrededor del 50%):"
        )

        rule_cols = st.columns(3)
        for col, card in zip(rule_cols, decision_rule_cards()):
            col.markdown(
                f'<div style="border:1px solid rgba(255,255,255,0.15); '
                f"border-radius:8px; padding:10px; text-align:center; "
                f'background:rgba(255,255,255,0.04);">'
                f'<div style="font-size:0.85rem; opacity:0.7; '
                f'margin-bottom:4px;">{card["range"]}</div>'
                f"{color_bg(card['label'])}</div>",
                unsafe_allow_html=True,
            )

        st.markdown(
            "- **< 45%:** No Bullying\n"
            "- **45% – 55%:** Incierto (modelos divididos, resultado no concluyente)\n"
            "- **> 55%:** Bullying"
        )

        # 4. Metricas de Modelos Entrenados
        st.header("Metricas de Modelos Entrenados")
        if not models_df.empty:
            st.dataframe(
                models_df,
                use_container_width=True,
                column_config={
                    "precision": st.column_config.NumberColumn("Precision", format="%.4f"),
                    "f1": st.column_config.NumberColumn("F1", format="%.4f"),
                    "recall": st.column_config.NumberColumn("Recall", format="%.4f"),
                    "accuracy": st.column_config.NumberColumn("Exactitud", format="%.4f"),
                },
            )
        else:
            st.info("No se pudieron cargar las metricas de los modelos.")


def main() -> None:
    st.set_page_config(page_title="Horus", page_icon="🧙‍♂️", layout="wide")

    st.title("Horus")
    st.write(
        "Horus es un modelo de clasificacion de texto que identifica si un texto es un caso "
        "de bullying o no."
    )

    apicall = ApiCalls()

    with st.spinner(text="Esperando respuesta del servidor..."):
        is_alive = apicall.healthcheck()

    if not is_alive:
        st.error("Error: No se pudo conectar con el servidor de Horus")
        st.stop()

    models_dict: dict = fetch_models(apicall.url)
    models_df = pd.DataFrame(models_dict).T
    if models_df.empty:
        st.error("Error: No se pudieron cargar las metricas de los modelos.")
        st.stop()
    models_df = models_df.sort_values(by="f1", ascending=False)

    st.session_state.setdefault("example_index", 0)
    st.session_state.setdefault("classification_snapshot", None)

    input_text, run_button = render_classification_input()

    if run_button:
        if input_text.strip() == "":
            st.error("Error: El texto ingresado esta vacio.")
            st.stop()
        with st.spinner(text="Obteniendo resultados..."):
            try:
                response = apicall.compare_text(input_text)
            except Exception as e:
                st.error(f"Error: {e}")
                st.stop()

        results = response.get("results") or []
        if not results:
            st.error("Error: No se obtuvo respuesta del servidor")
            st.stop()

        display_name_by_snake = {to_snake_case(name): name for name in models_df.index}

        failed_models = response.get("failed_models") or []
        failed_display_names = [
            display_name_by_snake.get(name, name)
            for name in failed_models
            if name not in {result["model"] for result in results}
        ]

        weights = f1_weights(
            {to_snake_case(name): float(f1) for name, f1 in models_df["f1"].items()}
        )
        weighted_score, majority, agreement_pct = compute_weighted_consensus(results, weights)
        mean_time_ms = sum(result["inference_time_ms"] for result in results) / len(results)
        model_names = [
            display_name_by_snake.get(result["model"], result["model"]) for result in results
        ]

        st.session_state["classification_snapshot"] = {
            "input_text": input_text,
            "results": results,
            "name_lookup": display_name_by_snake,
            "failed_display_names": failed_display_names,
            "model_options": ["Consenso ponderado"] + model_names,
            "weighted_score": weighted_score,
            "agreement_pct": agreement_pct,
            "majority": majority,
            "mean_time_ms": mean_time_ms,
        }
        st.session_state.pop("highlighted_model_selectbox", None)

    snapshot = st.session_state.get("classification_snapshot")
    if snapshot:
        render_classification_results(snapshot, models_df)

    render_guide(models_df)


main()
