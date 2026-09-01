"""Dibuja marcadores (círculos/óvalos) sobre una imagen a partir de detecciones o anotaciones."""
from __future__ import annotations

from PIL import Image, ImageDraw

from . import config


def draw_detections(image: Image.Image, detecciones: list, radius_scale: float = 1.0) -> Image.Image:
    """detecciones: lista de objetos/dicts con x, y, radio (normalizados 0-1) y tipo."""
    img = image.convert("RGB").copy()
    draw = ImageDraw.Draw(img)
    w, h = img.size

    for det in detecciones:
        x = det.x if hasattr(det, "x") else det["x"]
        y = det.y if hasattr(det, "y") else det["y"]
        radio = det.radio if hasattr(det, "radio") else det["radio"]
        tipo = det.tipo if hasattr(det, "tipo") else det.get("tipo", "fragmento")

        cx, cy = x * w, y * h
        r = max(radio * w * radius_scale, 4)
        color = config.TIPO_COLORS.get(tipo, "#FFD600")
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=max(2, int(r * 0.08)))

    return img


def draw_manual_circles(
    image: Image.Image, circulos: list[dict], radius_scale: float = 1.0, color: str = "#FFEB3B"
) -> Image.Image:
    """circulos: lista de {x, y, radio} normalizados, marcados a mano por el usuario."""
    img = image.convert("RGB").copy()
    draw = ImageDraw.Draw(img)
    w, h = img.size

    for c in circulos:
        cx, cy = c["x"] * w, c["y"] * h
        r = max(c["radio"] * w * radius_scale, 4)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=max(2, int(r * 0.08)))

    return img
