"""Correcciones del usuario sobre resultados ya analizados -> ejemplos etiquetados (positivo/
negativo) que se suman a los de Entrenamiento para reentrenar el clasificador por tinción."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from . import classifier, config, i18n, training_store


def _load() -> list[dict]:
    if not config.FEEDBACK_NOTES_PATH.exists():
        return []
    try:
        return json.loads(config.FEEDBACK_NOTES_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _save(samples: list[dict]) -> None:
    config.FEEDBACK_NOTES_PATH.write_text(
        json.dumps(samples, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def add_correction(tincion: str, features: dict, label: int, imagen_nombre: str = "") -> dict:
    """label: 1 = era un MP real (faltó marcarlo), 0 = no era un MP (falso positivo)."""
    samples = _load()
    sample = {
        "id": str(uuid.uuid4()),
        "fecha": datetime.now(timezone.utc).isoformat(),
        "tincion": tincion,
        "features": features,
        "label": label,
        "imagen_nombre": imagen_nombre,
    }
    samples.append(sample)
    _save(samples)
    return sample


def list_corrections(tincion: str | None = None) -> list[dict]:
    samples = _load()
    if tincion:
        samples = [s for s in samples if s["tincion"] == tincion]
    return sorted(samples, key=lambda s: s["fecha"], reverse=True)


def delete_correction(sample_id: str) -> None:
    samples = [s for s in _load() if s["id"] != sample_id]
    _save(samples)


def retrain(tincion: str) -> dict:
    """Junta los ejemplos de Entrenamiento (círculos) y de Correcciones para esta tinción, y
    reentrena el clasificador. Devuelve el resumen de classifier.train()."""
    muestras = training_store.extraer_ejemplos_etiquetados(tincion)
    muestras += [(c["features"], c["label"]) for c in list_corrections(tincion)]
    return classifier.train(tincion, muestras)


def explicar_insuficiente(resumen: dict) -> str:
    """Mensaje legible de qué falta para poder calibrar (alcanza con el mínimo total, no hace
    falta que haya ejemplos de ambas clases: ver classifier.train)."""
    n_pos, n_neg = resumen["n_pos"], resumen["n_neg"]
    return i18n.t(
        "insufficient_warning",
        pos=n_pos, neg=n_neg, total=n_pos + n_neg, minimo=config.MIN_SAMPLES_PARA_ENTRENAR,
    )
