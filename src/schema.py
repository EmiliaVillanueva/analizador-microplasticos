"""Modelos de datos para el resultado de un análisis."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Deteccion(BaseModel):
    x: float = Field(..., ge=0, le=1, description="Centro X normalizado (0-1)")
    y: float = Field(..., ge=0, le=1, description="Centro Y normalizado (0-1)")
    radio: float = Field(..., gt=0, le=1, description="Radio normalizado (0-1)")
    tipo: Literal["fibra", "fragmento", "pelicula_esfera"]
    confianza: float = Field(..., ge=0, le=1)
    # Features del candidato (área normalizada, aspect ratio, circularidad, solidez, nitidez,
    # color medio) — se guardan para poder reusarlas como ejemplo de entrenamiento sin
    # tener que recalcularlas al aplicar una corrección.
    features: dict = Field(default_factory=dict)


class AnalysisResult(BaseModel):
    conteo_total: int
    fibras: int
    fragmentos: int
    peliculas_esferas: int
    falsos_positivos_descartados: str
    detecciones: list[Deteccion] = Field(default_factory=list)

    imagen_nombre: str = ""
    tincion: str = ""
    error: str | None = None

    def coincide_totales(self) -> bool:
        return self.conteo_total == (self.fibras + self.fragmentos + self.peliculas_esferas)

    def to_report_text(self, lang: str = "es") -> str:
        from . import i18n  # import diferido: evita ciclo (i18n no depende de schema)

        def tr(key: str) -> str:
            return i18n.TRANSLATIONS[key].get(lang, i18n.TRANSLATIONS[key]["es"])

        fibras_label = i18n.TIPO_LABELS_EN["fibra"] if lang == "en" else "Fibras"
        fragmentos_label = i18n.TIPO_LABELS_EN["fragmento"] if lang == "en" else "Fragmentos"
        peliculas_label = i18n.TIPO_LABELS_EN["pelicula_esfera"] if lang == "en" else "Películas/Esferas"

        return (
            f"* {tr('report_total')}: {self.conteo_total}\n"
            f"* {tr('report_breakdown')}:\n"
            f"   * {fibras_label}: {self.fibras}\n"
            f"   * {fragmentos_label}: {self.fragmentos}\n"
            f"   * {peliculas_label}: {self.peliculas_esferas}\n"
            f"* {tr('report_falsos_positivos')}: {self.falsos_positivos_descartados}"
        )
