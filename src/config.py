"""Constantes y configuración compartida de la app."""
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
FEEDBACK_DIR = DATA_DIR / "feedback"
TRAINING_DIR = DATA_DIR / "training"
RESULTS_DIR = DATA_DIR / "results"
CLASSIFIERS_DIR = TRAINING_DIR / "classifiers"

FEEDBACK_NOTES_PATH = FEEDBACK_DIR / "labeled_samples.json"
TRAINING_METADATA_PATH = TRAINING_DIR / "metadata.json"
HSV_PROFILES_PATH = TRAINING_DIR / "hsv_profiles.json"

for _d in (DATA_DIR, FEEDBACK_DIR, TRAINING_DIR, RESULTS_DIR, CLASSIFIERS_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# Tinciones soportadas (el rango de color HSV de cada una vive en src/hsv_profiles.py).
TINCIONES = [
    "Autofluorescencia (UV/azul)",
    "Rodamina B",
    "Rojo Nilo (Nile Red)",
    "DAPI",
    "Otra / personalizada",
]

MORFOLOGIAS = ["fibra", "fragmento", "pelicula_esfera"]

TIPO_LABELS = {
    "fibra": "Fibras",
    "fragmento": "Fragmentos",
    "pelicula_esfera": "Películas/Esferas",
}

TIPO_COLORS = {
    "fibra": "#00E5FF",
    "fragmento": "#FF5252",
    "pelicula_esfera": "#FFD600",
}

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}

# --- Parámetros del motor de detección (cv_engine) ---
MIN_AREA_FRACTION = 0.00006   # área mínima de un candidato, como fracción del total de píxeles
MAX_AREA_FRACTION = 0.05      # sobre esta área se intenta separar el contorno (watershed) en partículas
# Tope duro: un contorno que supera MAX_AREA_FRACTION y NO se puede separar se considera una sola
# partícula grande y lo evalúa el clasificador, salvo que supere este tope (fondo/halo gigante).
MAX_AREA_HARD_FRACTION = 0.20

# Umbrales por defecto para el clasificador "es MP real" cuando todavía no hay suficientes
# ejemplos etiquetados para entrenar uno (arranque en frío).
DEFAULT_SHARPNESS_MIN = 0.35   # nitidez de borde relativa a la nitidez global de la imagen
DEFAULT_SOLIDITY_MIN = 0.35    # forma mínimamente compacta (descarta manchas muy irregulares/difusas)

# Clasificación de morfología (regla fija, no entrenable).
FIBRA_ASPECT_RATIO_MIN = 3.0
PELICULA_CIRCULARITY_MIN = 0.75
PELICULA_ASPECT_RATIO_MAX = 1.8

MIN_SAMPLES_PARA_ENTRENAR = 4  # mínimo de ejemplos (con ambas clases) para entrenar el clasificador
