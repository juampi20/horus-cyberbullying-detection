"""Constantes de configuración y datos demo compartidos por el frontend de Horus."""

from __future__ import annotations

# --- Configuración del consenso ---

UNCERTAINTY_MARGIN: float = 0.05

WEIGHT_AMPLIFICATION: float = 5.0

# --- Etiquetas de categorías para la UI ---

CATEGORY_LABELS: dict[str, str] = {
    "Bullying": "Bullying",
    "Not Bullying": "No Bullying",
    "Uncertain": "Incierto",
}

# --- Textos de ejemplo para el botón de demostración ---

EXAMPLES: list[str] = [
    "Andate de acá, nadie te aguanta, sos un pelotudo y no servís para nada.",
    "Sos un estúpido e inútil, ojalá te pudieras borrar del mundo.",
    "Sos un imbecil, no tenés dos dedos de frente y sos un desastre total.",
    "Boludo de mierda, no servís ni para limpiar pisos, sos un inútil total.",
    "Sos tan pelotudo que hasta los perros te evitan por la calle.",
    "Sos tan tonto que no te das cuenta de que todos te evitan.",
    "Tenés razón en algo, pero sos un poco molesto.",
    "No entiendo por qué te enojás tanto por todo.",
    "Que tengas un lindo día, me encantó hablar con vos hoy.",
    "Estoy de acuerdo con tu opinión, creo que es una buena idea.",
    "Gracias por tu ayuda, fue muy valioso tu aporte al equipo.",
    "Hola, ¿cómo estás? Espero que tengas un buen fin de semana.",
]
