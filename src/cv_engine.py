"""Segmentación y extracción de features por partícula candidata (sin IA, solo OpenCV).

El pipeline es: umbral de color/brillo (según el rango HSV de la tinción) -> limpieza
morfológica -> contornos -> por cada contorno, medir tamaño, forma y nitidez de borde.
Esas features son las que después decide si es un MP real o un artefacto (clasificador o
reglas por defecto, ver classifier.py) y de qué morfología es (regla fija, ver clasificar_morfologia).
"""
from __future__ import annotations

import cv2
import numpy as np

from . import config


def decode_image(image_bytes: bytes) -> np.ndarray:
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("No se pudo decodificar la imagen (formato no soportado o archivo corrupto).")
    return img


def _color_mask(hsv: np.ndarray, profile: dict) -> np.ndarray:
    h, w = hsv.shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)
    sat_min = profile.get("sat_min", 20)
    val_min = profile.get("val_min", 50)
    for hue_min, hue_max in profile.get("hue_ranges", [[0, 179]]):
        lower = np.array([hue_min, sat_min, val_min], dtype=np.uint8)
        upper = np.array([hue_max, 255, 255], dtype=np.uint8)
        mask |= cv2.inRange(hsv, lower, upper)
    return mask


def _clean_mask(mask: np.ndarray) -> np.ndarray:
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    return mask


def _aspect_ratio(contour: np.ndarray) -> float:
    if len(contour) >= 5:
        (_, _), (ma, mb), _ = cv2.fitEllipse(contour)
        short, long_ = sorted((ma, mb))
    else:
        (_, _), (w, h), _ = cv2.minAreaRect(contour)
        short, long_ = sorted((w, h))
    return long_ / max(short, 1e-6)


def _robust_lap_scale(gray: np.ndarray) -> float:
    """Escala de referencia para normalizar la nitidez local. Un par de píxeles extremos (polvo,
    ruido de sensor) puede disparar la varianza del Laplaciano de toda la imagen y aplastar la
    nitidez normalizada de TODAS las partículas reales a valores cercanos a 0 — por eso se usa un
    percentil robusto en vez de la varianza completa, que es muy sensible a esos outliers."""
    lap = cv2.Laplacian(gray, cv2.CV_64F)
    p90 = float(np.percentile(np.abs(lap), 90))
    return (p90 ** 2) or 1.0


def _edge_sharpness(gray: np.ndarray, mask_full: np.ndarray, contour: np.ndarray, global_lap_var: float) -> float:
    """Nitidez de borde relativa: Laplaciano en un anillo alrededor del contorno, normalizado
    por la nitidez general de la imagen (para que no dependa de la exposición/ganancia)."""
    x, y, w, h = cv2.boundingRect(contour)
    pad = max(3, int(0.3 * max(w, h)))
    x0, y0 = max(0, x - pad), max(0, y - pad)
    x1, y1 = min(gray.shape[1], x + w + pad), min(gray.shape[0], y + h + pad)
    if x1 <= x0 or y1 <= y0:
        return 0.0

    local_mask = (mask_full[y0:y1, x0:x1] > 0).astype(np.uint8)
    dilated = cv2.dilate(local_mask, np.ones((5, 5), np.uint8))
    eroded = cv2.erode(local_mask, np.ones((3, 3), np.uint8))
    ring = (dilated - eroded) > 0
    if not ring.any():
        return 0.0

    local_gray = gray[y0:y1, x0:x1].astype(np.float64)
    lap = cv2.Laplacian(local_gray, cv2.CV_64F)
    local_var = float(lap[ring].var()) if ring.sum() > 1 else 0.0
    return local_var / (global_lap_var + 1e-6)


def _contour_features(
    hsv: np.ndarray, gray: np.ndarray, contour_mask: np.ndarray, contour: np.ndarray,
    global_lap_var: float, w: int, h: int,
) -> dict | None:
    """Features geométricas y de color de UN contorno ya segmentado. Común a detectar_candidatos
    y a features_for_region para que ambas fuentes de ejemplos sean comparables entre sí."""
    area = cv2.contourArea(contour)
    if area <= 0:
        return None

    perimeter = cv2.arcLength(contour, True)
    circularity = min(1.0, (4 * np.pi * area) / (perimeter ** 2)) if perimeter > 0 else 0.0

    hull = cv2.convexHull(contour)
    hull_area = cv2.contourArea(hull)
    solidity = area / hull_area if hull_area > 0 else 0.0

    moments = cv2.moments(contour)
    if moments["m00"] == 0:
        return None
    cx = moments["m10"] / moments["m00"]
    cy = moments["m01"] / moments["m00"]

    hsv_vals = hsv[contour_mask > 0]
    if hsv_vals.size == 0:
        return None
    hue_mean, sat_mean, val_mean = (float(v) for v in hsv_vals.mean(axis=0))

    sharpness = _edge_sharpness(gray, contour_mask, contour, global_lap_var)

    return {
        "x": cx / w,
        "y": cy / h,
        "radio": float(np.sqrt(area / np.pi)) / w,
        "area_norm": area / (w * h),
        "aspect_ratio": _aspect_ratio(contour),
        "circularity": circularity,
        "solidity": solidity,
        "sharpness": sharpness,
        "hue_mean": hue_mean,
        "sat_mean": sat_mean / 255.0,
        "val_mean": val_mean / 255.0,
    }


def detectar_candidatos(image_bgr: np.ndarray, profile: dict) -> tuple[list[dict], int]:
    """Devuelve (candidatos, descartados_por_tamaño). Cada candidato es un dict con posición
    normalizada, features geométricas y de color, listo para clasificar."""
    h, w = image_bgr.shape[:2]
    total_px = h * w
    min_area = max(6.0, config.MIN_AREA_FRACTION * total_px)
    max_area = config.MAX_AREA_FRACTION * total_px
    hard_max_area = config.MAX_AREA_HARD_FRACTION * total_px

    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    global_lap_var = _robust_lap_scale(gray)

    mask = _clean_mask(_color_mask(hsv, profile))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    candidatos = []
    descartados_tamano = 0
    for c in contours:
        area = cv2.contourArea(c)

        if area > max_area:
            # Pueden ser varias partículas pegadas (se intenta separarlas) o UNA sola partícula
            # grande, que no tiene nada que separar: en ese caso se conserva como candidata y la
            # decide el clasificador, salvo que supere el tope duro (fondo/halo gigante).
            piezas = _separar_recursivo(c, h, w, min_area, max_area, hard_max_area)
            if not piezas and area <= hard_max_area:
                whole_mask = np.zeros((h, w), dtype=np.uint8)
                cv2.drawContours(whole_mask, [c], -1, 255, thickness=cv2.FILLED)
                piezas = [(whole_mask, c)]
            if not piezas:
                descartados_tamano += 1
                continue
            for pieza_mask, pieza_contour in piezas:
                feats = _contour_features(hsv, gray, pieza_mask, pieza_contour, global_lap_var, w, h)
                if feats is not None:
                    candidatos.append(feats)
            continue

        if area < min_area:
            if area >= 2:  # ruido de 0-1px no cuenta como "descartado", es solo grano de la máscara
                descartados_tamano += 1
            continue

        contour_mask = np.zeros((h, w), dtype=np.uint8)
        cv2.drawContours(contour_mask, [c], -1, 255, thickness=cv2.FILLED)
        feats = _contour_features(hsv, gray, contour_mask, c, global_lap_var, w, h)
        if feats is not None:
            candidatos.append(feats)

    return candidatos, descartados_tamano


MAX_SPLIT_DEPTH = 4


def _separar_recursivo(
    contour: np.ndarray, h: int, w: int, min_area: float, max_area: float,
    hard_max_area: float, depth: int = 0,
) -> list[tuple[np.ndarray, np.ndarray]]:
    """Separa un contorno grande en piezas dentro del rango de tamaño válido, volviendo a
    intentar sobre cualquier pieza que siga siendo demasiado grande (varias partículas pegadas no
    siempre se separan de un solo intento de watershed). Una pieza grande que ya no se puede
    separar más es una sola partícula grande: se conserva si no supera hard_max_area. Se descartan
    las piezas muy chicas (recortes residuales del propio corte)."""
    piezas_crudas = _split_large_contour(contour, h, w)
    if not piezas_crudas:
        return []

    resultado = []
    for pieza_mask, pieza_contour in piezas_crudas:
        pieza_area = cv2.contourArea(pieza_contour)
        if min_area <= pieza_area <= max_area:
            resultado.append((pieza_mask, pieza_contour))
        elif pieza_area > max_area:
            sub = []
            if depth < MAX_SPLIT_DEPTH:
                sub = _separar_recursivo(pieza_contour, h, w, min_area, max_area, hard_max_area, depth + 1)
            if sub:
                resultado.extend(sub)
            elif pieza_area <= hard_max_area:
                resultado.append((pieza_mask, pieza_contour))
        # pieza_area < min_area: recorte residual del watershed, se descarta
    return resultado


def _split_large_contour(contour: np.ndarray, h: int, w: int) -> list[tuple[np.ndarray, np.ndarray]]:
    """Separa un contorno demasiado grande en las partículas individuales que probablemente lo
    componen (varias manchas que se tocan y la máscara de color las une en una sola), usando
    watershed sobre la transformada de distancia. Devuelve una lista de (máscara, contorno) por
    partícula separada, o [] si no se pudo separar en más de una pieza."""
    x, y, bw, bh = cv2.boundingRect(contour)
    local_mask = np.zeros((bh, bw), dtype=np.uint8)
    cv2.drawContours(local_mask, [contour], -1, 255, thickness=cv2.FILLED, offset=(-x, -y))

    dist = cv2.distanceTransform(local_mask, cv2.DIST_L2, 5)
    if dist.max() <= 0:
        return []
    _, picos = cv2.threshold(dist, 0.4 * dist.max(), 255, 0)
    picos = picos.astype(np.uint8)
    n_picos, markers = cv2.connectedComponents(picos)
    if n_picos <= 2:  # <=1 pico real (0 = fondo) -> no hay nada que separar
        return []

    markers = markers + 1
    markers[local_mask == 0] = 0
    color_local = cv2.cvtColor(local_mask, cv2.COLOR_GRAY2BGR)
    cv2.watershed(color_local, markers)

    piezas = []
    for label in range(2, n_picos + 1):
        pieza_local = np.uint8(markers == label) * 255
        sub_contours, _ = cv2.findContours(pieza_local, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not sub_contours:
            continue
        sub_contour_local = max(sub_contours, key=cv2.contourArea)
        pieza_full = np.zeros((h, w), dtype=np.uint8)
        pieza_full[y:y + bh, x:x + bw] = pieza_local
        sub_contour_full = sub_contour_local + np.array([[x, y]])
        piezas.append((pieza_full, sub_contour_full))
    return piezas


def features_for_region(image_bgr: np.ndarray, cx_norm: float, cy_norm: float, r_norm: float, profile: dict) -> dict:
    """Features para un punto marcado a mano (Correcciones -> 'faltó marcarlo'). Primero busca la
    mancha de color real más cercana (mismo umbral que detectar_candidatos) para que sus features
    sean comparables a las de un candidato detectado automáticamente. Si el motor de color no ve
    nada ahí, usa el círculo dibujado como aproximación (menos confiable: al ser una forma
    perfecta, su solidez/nitidez no reflejan la partícula real)."""
    h, w = image_bgr.shape[:2]
    cx, cy, r = cx_norm * w, cy_norm * h, max(r_norm * w, 3)

    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    global_lap_var = _robust_lap_scale(gray)

    color_mask = _clean_mask(_color_mask(hsv, profile))
    contours, _ = cv2.findContours(color_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    best_contour, best_dist = None, None
    for c in contours:
        moments = cv2.moments(c)
        if moments["m00"] == 0:
            continue
        ccx, ccy = moments["m10"] / moments["m00"], moments["m01"] / moments["m00"]
        dist = ((ccx - cx) ** 2 + (ccy - cy) ** 2) ** 0.5
        if dist <= r * 2 and (best_dist is None or dist < best_dist):
            best_contour, best_dist = c, dist

    if best_contour is not None:
        contour_mask = np.zeros((h, w), dtype=np.uint8)
        cv2.drawContours(contour_mask, [best_contour], -1, 255, thickness=cv2.FILLED)
        feats = _contour_features(hsv, gray, contour_mask, best_contour, global_lap_var, w, h)
        if feats is not None:
            feats["metodo"] = "color"
            return feats

    # El umbral de color/brillo configurado para esta tinción no detectó nada ahí: no hay mancha
    # real para medir. Se aproxima con el círculo dibujado, pero avisamos vía "metodo" para que la
    # UI le sugiera al usuario bajar el umbral de color en vez de (o además de) esta corrección.
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.circle(mask, (int(round(cx)), int(round(cy))), int(round(r)), 255, thickness=cv2.FILLED)
    contours2, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours2:
        return {
            "x": cx_norm, "y": cy_norm, "radio": r_norm,
            "area_norm": 0.0, "aspect_ratio": 1.0, "circularity": 1.0, "solidity": 1.0,
            "sharpness": 0.0, "hue_mean": 0.0, "sat_mean": 0.0, "val_mean": 0.0,
            "metodo": "circulo_aproximado",
        }
    c = max(contours2, key=cv2.contourArea)
    feats = _contour_features(hsv, gray, mask, c, global_lap_var, w, h)
    feats = feats or {
        "x": cx_norm, "y": cy_norm, "radio": r_norm,
        "area_norm": 0.0, "aspect_ratio": 1.0, "circularity": 1.0, "solidity": 1.0,
        "sharpness": 0.0, "hue_mean": 0.0, "sat_mean": 0.0, "val_mean": 0.0,
    }
    feats["metodo"] = "circulo_aproximado"
    return feats


def clasificar_morfologia(features: dict) -> str:
    aspect_ratio = features["aspect_ratio"]
    circularity = features["circularity"]
    if aspect_ratio >= config.FIBRA_ASPECT_RATIO_MIN:
        return "fibra"
    if circularity >= config.PELICULA_CIRCULARITY_MIN and aspect_ratio <= config.PELICULA_ASPECT_RATIO_MAX:
        return "pelicula_esfera"
    return "fragmento"


FEATURE_KEYS = [
    "area_norm", "aspect_ratio", "circularity", "solidity", "sharpness", "hue_mean", "sat_mean", "val_mean",
]


def feature_vector(features: dict) -> list[float]:
    return [float(features.get(k, 0.0)) for k in FEATURE_KEYS]
