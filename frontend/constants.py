"""Constantes de configuracion y datos demo compartidos por el frontend de Horus."""

from __future__ import annotations

# --- Configuracion del consenso ---

UNCERTAINTY_MARGIN: float = 0.05

WEIGHT_AMPLIFICATION: float = 5.0

# --- Cooldown del boton de clasificacion ---

RUN_COOLDOWN_SECONDS: float = 1.0

# --- Etiquetas de categorias para la UI ---

CATEGORY_LABELS: dict[str, str] = {
    "Bullying": "Bullying",
    "Not Bullying": "No Bullying",
    "Uncertain": "Incierto",
}

# --- Etiquetas de proveedores de traduccion para la UI ---

TRANSLATION_PROVIDER_LABELS: dict[str, str] = {
    "deepl": "DeepL",
    "google": "Google",
    "mymemory": "MyMemory",
}

# --- Textos de ejemplo para el boton de demostracion ---

# Veredictos verificados contra la API real: 3 No Bullying, 3 Incierto (45-55%), 3 Bullying.
EXAMPLES: list[str] = [
    "Espero que te mejores pronto, cuidate mucho.",
    "Me alegro mucho por vos, te lo mereces.",
    "Buen trabajo hoy, se nota el esfuerzo que le pusiste.",
    "No entiendo por que te enojas tanto por todo.",
    "Por que te pones mal cuando te corrigen.",
    "Te tomas todo como una critica.",
    "Sos un idiota, un desastre total.",
    "Andate de aca que sos un pelotudo, no servis para nada.",
    "Sos un estupido e inutil, ojala te fueras de aca.",
]
