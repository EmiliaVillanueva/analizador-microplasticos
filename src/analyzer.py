"""Orquesta el análisis de una o varias imágenes con el motor de visión clásico (cv_engine)."""
from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from . import classifier, config, cv_engine, hsv_profiles, i18n
from .schema import AnalysisResult, Deteccion


def list_images_in_folder(folder: str) -> list[Path]:
    path = Path(folder)
    if not path.is_dir():
        return []
    return sorted(
        p for p in path.iterdir()
        if p.is_file() and p.suffix.lower() in config.IMAGE_EXTENSIONS
    )


def analyze_image(image_bytes: bytes, filename: str, tincion: str, lang: str = "es") -> AnalysisResult:
    try:
        img = cv_engine.decode_image(image_bytes)
    except ValueError as exc:
        return AnalysisResult(
            conteo_total=0, fibras=0, fragmentos=0, peliculas_esferas=0,
            falsos_positivos_descartados="", detecciones=[],
            imagen_nombre=filename, tincion=tincion, error=str(exc),
        )

    profile = hsv_profiles.get_profile(tincion)
    candidatos, descartados_tamano = cv_engine.detectar_candidatos(img, profile)

    detecciones: list[Deteccion] = []
    descartados_clasificador = 0
    for cand in candidatos:
        es_real, confianza = classifier.predict(tincion, cand)
        if not es_real:
            descartados_clasificador += 1
            continue
        tipo = cv_engine.clasificar_morfologia(cand)
        detecciones.append(Deteccion(
            x=cand["x"], y=cand["y"], radio=min(cand["radio"], 1.0),
            tipo=tipo, confianza=confianza, features=cand,
        ))

    partes = []
    if descartados_tamano:
        partes.append(i18n.t("discard_size", lang=lang, n=descartados_tamano))
    if descartados_clasificador:
        partes.append(i18n.t("discard_classifier", lang=lang, n=descartados_clasificador))
    descartados_texto = "; ".join(partes) if partes else i18n.t("discard_none", lang=lang)

    fibras = sum(1 for d in detecciones if d.tipo == "fibra")
    fragmentos = sum(1 for d in detecciones if d.tipo == "fragmento")
    peliculas = sum(1 for d in detecciones if d.tipo == "pelicula_esfera")

    return AnalysisResult(
        conteo_total=len(detecciones),
        fibras=fibras,
        fragmentos=fragmentos,
        peliculas_esferas=peliculas,
        falsos_positivos_descartados=descartados_texto,
        detecciones=detecciones,
        imagen_nombre=filename,
        tincion=tincion,
    )


def analyze_batch(
    items: list[tuple[str, bytes]],
    tincion: str,
    on_progress: Callable[[int, int, str], None] | None = None,
    lang: str = "es",
) -> list[AnalysisResult]:
    """items: lista de (nombre_archivo, bytes). Un error en una imagen no interrumpe el resto del lote."""
    results: list[AnalysisResult] = []
    total = len(items)
    for i, (filename, data) in enumerate(items, start=1):
        if on_progress:
            on_progress(i - 1, total, filename)
        try:
            result = analyze_image(data, filename, tincion, lang=lang)
        except Exception as exc:  # noqa: BLE001
            result = AnalysisResult(
                conteo_total=0, fibras=0, fragmentos=0, peliculas_esferas=0,
                falsos_positivos_descartados="", detecciones=[],
                imagen_nombre=filename, tincion=tincion, error=str(exc),
            )
        results.append(result)
        if on_progress:
            on_progress(i, total, filename)
    return results
