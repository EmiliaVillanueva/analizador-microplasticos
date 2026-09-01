"""Persistencia de imágenes de referencia (ejemplos marcados a mano) y su conversión en
ejemplos etiquetados (features + positivo/negativo) para entrenar el clasificador."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from . import config, cv_engine, hsv_profiles


def _load() -> list[dict]:
    if not config.TRAINING_METADATA_PATH.exists():
        return []
    try:
        return json.loads(config.TRAINING_METADATA_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _save(items: list[dict]) -> None:
    config.TRAINING_METADATA_PATH.write_text(
        json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def add_example(
    tincion: str,
    image_bytes: bytes,
    ext: str,
    circulos: list[dict],
    nota: str = "",
) -> dict:
    """circulos: lista de {x, y, radio} normalizados (0-1), marcados a mano por el usuario como MP verdadero."""
    example_id = str(uuid.uuid4())
    filename = f"{example_id}{ext}"
    (config.TRAINING_DIR / filename).write_bytes(image_bytes)

    items = _load()
    item = {
        "id": example_id,
        "fecha": datetime.now(timezone.utc).isoformat(),
        "tincion": tincion,
        "archivo": filename,
        "circulos": circulos,
        "nota": nota.strip(),
    }
    items.append(item)
    _save(items)
    return item


def list_examples(tincion: str | None = None) -> list[dict]:
    items = _load()
    if tincion:
        items = [i for i in items if i["tincion"] == tincion]
    return sorted(items, key=lambda i: i["fecha"], reverse=True)


def delete_example(example_id: str) -> None:
    items = _load()
    remaining = []
    for item in items:
        if item["id"] == example_id:
            path = config.TRAINING_DIR / item["archivo"]
            if path.exists():
                path.unlink()
        else:
            remaining.append(item)
    _save(remaining)


def example_image_path(item: dict):
    return config.TRAINING_DIR / item["archivo"]


def _dentro_de_algun_circulo(cand: dict, circulos: list[dict]) -> bool:
    for c in circulos:
        dist = ((cand["x"] - c["x"]) ** 2 + (cand["y"] - c["y"]) ** 2) ** 0.5
        if dist <= c["radio"] * 1.3:  # margen: el centro del contorno detectado no siempre cae justo en el medio
            return True
    return False


def extraer_ejemplos_etiquetados(tincion: str) -> list[tuple[dict, int]]:
    """Corre el motor de detección sobre cada imagen de referencia guardada para esta tinción.
    Los candidatos que caen dentro de un círculo marcado a mano son positivos (MP real);
    los que el motor detecta pero el usuario no marcó son negativos (artefacto)."""
    profile = hsv_profiles.get_profile(tincion)
    muestras: list[tuple[dict, int]] = []
    for ex in list_examples(tincion):
        path = example_image_path(ex)
        if not path.exists():
            continue
        try:
            img = cv_engine.decode_image(path.read_bytes())
        except ValueError:
            continue
        candidatos, _ = cv_engine.detectar_candidatos(img, profile)
        for cand in candidatos:
            label = 1 if _dentro_de_algun_circulo(cand, ex["circulos"]) else 0
            muestras.append((cand, label))
    return muestras
