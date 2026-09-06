"""Constantes de configuracion y datos demo compartidos por el frontend de Horus."""

from __future__ import annotations

# --- Configuracion del consenso ---

UNCERTAINTY_MARGIN: float = 0.05

WEIGHT_AMPLIFICATION: float = 5.0

# --- Etiquetas de categorias para la UI ---

CATEGORY_LABELS: dict[str, str] = {
    "Bullying": "Bullying",
    "Not Bullying": "No Bullying",
    "Uncertain": "Incierto",
}

# --- Textos de ejemplo para el boton de demostracion ---

EXAMPLES: list[str] = [
    "Andate de aca, nadie te aguanta, sos un pelotudo y no servis para nada.",
    "Sos un estupido e inutil, ojala te pudieras borrar del mundo.",
    "Sos un imbecil, no tenes dos dedos de frente y sos un desastre total.",
    "Boludo de mierda, no servis ni para limpiar pisos, sos un inutil total.",
    "Sos tan pelotudo que hasta los perros te evitan por la calle.",
    "Sos tan tonto que no te das cuenta de que todos te evitan.",
    "Tenes razon en algo, pero sos un poco molesto.",
    "No entiendo por que te enojas tanto por todo.",
    "Que tengas un lindo dia, me encanto hablar con vos hoy.",
    "Estoy de acuerdo con tu opinion, creo que es una buena idea.",
    "Gracias por tu ayuda, fue muy valioso tu aporte al equipo.",
    "Hola, ¿como estas? Espero que tengas un buen fin de semana.",
]
