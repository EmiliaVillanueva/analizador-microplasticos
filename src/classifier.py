"""Clasificador 'es un MP real vs. artefacto' por tinción.

Sin ejemplos etiquetados usa una regla por defecto (nitidez de borde + solidez de forma, ver
config.DEFAULT_SHARPNESS_MIN / DEFAULT_SOLIDITY_MIN) para poder analizar desde el primer uso.

Con al menos config.MIN_SAMPLES_PARA_ENTRENAR ejemplos:
- si hay ejemplos de ambas clases (positivo y negativo), entrena una regresión logística liviana
  sobre las features geométricas y de color de cv_engine.
- si todos los ejemplos son de una sola clase, no se puede entrenar un clasificador binario, pero
  se ajusta el umbral por defecto según lo que muestran esos ejemplos (más permisivo si todos son
  MP reales confirmados, más estricto si todos son artefactos confirmados).
"""
from __future__ import annotations

import json
import re

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from . import config, cv_engine


def _slug(tincion: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", tincion.lower()).strip("_")


def _model_path(tincion: str):
    return config.CLASSIFIERS_DIR / f"{_slug(tincion)}.joblib"


def _thresholds_path(tincion: str):
    return config.CLASSIFIERS_DIR / f"{_slug(tincion)}_thresholds.json"


def has_trained_model(tincion: str) -> bool:
    return _model_path(tincion).exists()


def has_calibrated_thresholds(tincion: str) -> bool:
    return _thresholds_path(tincion).exists()


def status(tincion: str) -> str:
    if has_trained_model(tincion):
        return "clasificador"
    if has_calibrated_thresholds(tincion):
        return "umbral_ajustado"
    return "por_defecto"


def _load_thresholds(tincion: str) -> dict | None:
    path = _thresholds_path(tincion)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _fallback_predict(features: dict, thresholds: dict | None = None) -> tuple[bool, float]:
    sharpness_min = thresholds["sharpness_min"] if thresholds else config.DEFAULT_SHARPNESS_MIN
    solidity_min = thresholds["solidity_min"] if thresholds else config.DEFAULT_SOLIDITY_MIN

    es_real = features["sharpness"] >= sharpness_min and features["solidity"] >= solidity_min
    # Confianza heurística: qué tan por encima de los umbrales está, acotada a un rango razonable.
    margen = (features["sharpness"] - sharpness_min) + (features["solidity"] - solidity_min)
    confianza = float(np.clip(0.55 + margen * 0.3, 0.2, 0.9))
    return es_real, confianza if es_real else 1 - confianza


def predict(tincion: str, features: dict) -> tuple[bool, float]:
    path = _model_path(tincion)
    if path.exists():
        try:
            model = joblib.load(path)
            vec = np.array([cv_engine.feature_vector(features)])
            proba_real = float(model.predict_proba(vec)[0][1])
            return proba_real >= 0.5, proba_real
        except (OSError, ValueError, EOFError):
            pass  # modelo corrupto/ilegible: seguir con el umbral ajustado o el de por defecto
    return _fallback_predict(features, _load_thresholds(tincion))


def train(tincion: str, samples: list[tuple[dict, int]]) -> dict:
    """samples: lista de (features, label) con label 1 = MP real, 0 = artefacto."""
    labels = [label for _, label in samples]
    n_pos, n_neg = labels.count(1), labels.count(0)

    if len(samples) < config.MIN_SAMPLES_PARA_ENTRENAR:
        return {"trained": False, "mode": None, "n_pos": n_pos, "n_neg": n_neg}

    if n_pos > 0 and n_neg > 0:
        x = np.array([cv_engine.feature_vector(f) for f, _ in samples])
        y = np.array(labels)
        model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, class_weight="balanced"))
        model.fit(x, y)
        joblib.dump(model, _model_path(tincion))
        _thresholds_path(tincion).unlink(missing_ok=True)  # el clasificador reemplaza al umbral ajustado
        return {"trained": True, "mode": "clasificador", "n_pos": n_pos, "n_neg": n_neg}

    # Todos los ejemplos son de una sola clase: no alcanza para un clasificador binario, pero se
    # puede correr el umbral por defecto hacia lo que muestran estos ejemplos confirmados.
    feats = [f for f, _ in samples]
    sharpness_vals = [f["sharpness"] for f in feats]
    solidity_vals = [f["solidity"] for f in feats]

    if n_pos > 0:  # todos MP reales confirmados -> umbral más permisivo (no rechazarlos)
        sharpness_min = min(sharpness_vals) * 0.9
        solidity_min = min(solidity_vals) * 0.9
    else:  # todos artefactos confirmados -> umbral más estricto (rechazarlos)
        sharpness_min = max(sharpness_vals) * 1.1
        solidity_min = max(solidity_vals) * 1.1

    thresholds = {
        "sharpness_min": round(max(0.0, sharpness_min), 4),
        "solidity_min": round(max(0.0, min(solidity_min, 1.0)), 4),
    }
    _thresholds_path(tincion).write_text(json.dumps(thresholds, ensure_ascii=False, indent=2), encoding="utf-8")
    _model_path(tincion).unlink(missing_ok=True)
    return {"trained": True, "mode": "umbral_ajustado", "n_pos": n_pos, "n_neg": n_neg, "thresholds": thresholds}


def delete_model(tincion: str) -> None:
    """Vuelve esta tinción a los umbrales por defecto (borra clasificador y umbral ajustado)."""
    _model_path(tincion).unlink(missing_ok=True)
    _thresholds_path(tincion).unlink(missing_ok=True)
