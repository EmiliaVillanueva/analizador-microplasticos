"""Perfiles de color HSV por tinción: qué rango de color/brillo corresponde a la señal esperada.

Rangos en escala de OpenCV: H 0-179, S 0-255, V 0-255. `hue_ranges` es una lista de [min, max]
para poder cubrir tonos que envuelven el 0 (rojos), usando dos rangos en vez de uno.
"""
from __future__ import annotations

import json

from . import config

# Solo "Autofluorescencia (UV/azul)" fue validada con muestras reales (brillo mínimo 32); los
# rangos de las demás tinciones son puntos de partida razonables, no valores validados.
DEFAULT_PROFILES: dict[str, dict] = {
    "Autofluorescencia (UV/azul)": {"hue_ranges": [[78, 140]], "sat_min": 40, "val_min": 32},
    "Rodamina B": {"hue_ranges": [[0, 18], [160, 179]], "sat_min": 60, "val_min": 55},
    "Rojo Nilo (Nile Red)": {"hue_ranges": [[0, 22], [155, 179]], "sat_min": 55, "val_min": 55},
    "DAPI": {"hue_ranges": [[85, 115]], "sat_min": 30, "val_min": 50},
    "Otra / personalizada": {"hue_ranges": [[0, 179]], "sat_min": 20, "val_min": 60},
}


def _load_overrides() -> dict:
    if not config.HSV_PROFILES_PATH.exists():
        return {}
    try:
        return json.loads(config.HSV_PROFILES_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _save_overrides(overrides: dict) -> None:
    config.HSV_PROFILES_PATH.write_text(
        json.dumps(overrides, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def get_profile(tincion: str) -> dict:
    overrides = _load_overrides()
    if tincion in overrides:
        return overrides[tincion]
    return DEFAULT_PROFILES.get(tincion, DEFAULT_PROFILES["Otra / personalizada"])


def set_profile(tincion: str, profile: dict) -> None:
    overrides = _load_overrides()
    overrides[tincion] = profile
    _save_overrides(overrides)


def reset_profile(tincion: str) -> None:
    overrides = _load_overrides()
    overrides.pop(tincion, None)
    _save_overrides(overrides)


def is_customized(tincion: str) -> bool:
    return tincion in _load_overrides()
