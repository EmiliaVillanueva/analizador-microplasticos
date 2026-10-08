# Microplastics Analyzer / Analizador de Microplásticos

[English](#english) · [Español](#español)

---

## English

A local web app (Streamlit) that detects and counts microplastics (MPs) in fluorescence
microscopy images. The engine runs **100 % locally, free of charge and offline**: classical image
processing (OpenCV) based on colour, brightness, shape and edge sharpness, plus a light classifier
(scikit-learn) that you can calibrate with your own reference photos and corrections. It uses no
third-party AI service and needs no API key.

Features: stain selection, single images or whole folders in batch (with progress bar), a
side-by-side viewer, manual reference marking, error correction that feeds back into the
classifier, a copy-to-Excel results table, and an English/Spanish interface.

### Quick start

Requires Python 3.11 or newer (developed on 3.13) and Git.

```bash
git clone https://github.com/EmiliaVillanueva/analizador-microplasticos.git
cd analizador-microplasticos
pip install -r requirements.txt
python -m streamlit run app.py
```

The app opens at `http://localhost:8501`. Use `python -m streamlit` rather than plain
`streamlit` — on Windows the latter often fails with "not recognised" because pip's script folder
is not on the PATH. Choose the language in the sidebar.

### How detection works

1. **Colour segmentation** — the image is converted to HSV and thresholded with a stain-specific
   window; the mask is cleaned by morphological opening/closing (3 × 3 elliptical kernel) and
   candidate particles are taken as external contours.
2. **Size filtering** — candidates smaller than a minimum area are discarded. A contour larger than
   the *split threshold* is usually several bright particles joined by a background halo that
   passes the colour threshold: it is first re-thresholded at a higher brightness (Otsu within
   the blob, repeated if needed) to keep the bright *cores*, which must exceed a larger minimum
   area. If that does not yield at least two cores, the contour is cut by a distance-transform
   watershed (recursive, up to 4 levels); a large contour that cannot be split is kept as a
   single particle unless it exceeds the *hard cap* (background/halo).
3. **Features** — normalised area, aspect ratio, circularity, solidity, edge sharpness (Laplacian
   variance in a ring around the contour, normalised by a robust per-image scale) and mean H, S, V.
4. **Real particle vs. artefact** — default rule (sharpness ≥ 0.35 and solidity ≥ 0.35) or, once
   at least 4 labelled examples exist, a logistic-regression classifier trained per stain.
5. **Morphology** — fixed rules: fibre (aspect ratio ≥ 3.0), film/sphere (circularity ≥ 0.75 and
   aspect ratio ≤ 1.8), fragment (everything else).

### Default parameters (reproducibility)

| Parameter | Value |
|---|---|
| Autofluorescence (UV/blue): hue / saturation / brightness | H 78–140 · S ≥ 40 · V ≥ 32 (OpenCV scale: H 0–179, S/V 0–255) |
| Minimum particle area | 6 × 10⁻⁵ of the image area |
| Watershed split threshold | 5 % of the image area |
| Hard cap for unsplittable contours | 20 % of the image area |
| Minimum area of a bright core inside a halo blob | 4 × 10⁻⁴ of the image area (≈ 15 µm at 0.463 µm/px, 1920 × 1080) |
| Default real-particle rule | sharpness ≥ 0.35 and solidity ≥ 0.35 |
| Minimum examples to calibrate | 4 |

Only the **Autofluorescence (UV/blue)** defaults were validated with real samples. The ranges for
Rhodamine B, Nile Red, DAPI and "Other" are reasonable starting points, not validated values —
tune them on the *Settings* page for your own images.

**Physical size.** Area thresholds are fractions of the image area, so the smallest detectable size
depends on image resolution and pixel calibration:
`D_min = sqrt(4 · 6×10⁻⁵ · W · H / π) × (µm per pixel)`.
Example: a 1920 × 1080 image at 0.463 µm/px (216 px = 100 µm) gives 12.6 px ≈ 5.8 µm. Report the
resolution and calibration you used.

### Improving detection

- **Training** — upload a photo and mark where the real MPs are; everything detected outside the
  marked circles becomes a negative example.
- **Corrections** — after an analysis, mark false positives, or add particles that were missed.
- **Settings → Recalibrate** — combines both and trains the classifier for that stain.

### Data and known limitations

- Reference photos, corrections, trained classifiers and any colour range you change are stored in
  `data/`, which is **not versioned**. A fresh clone therefore starts from the defaults above and
  will not reproduce results obtained with a locally calibrated installation unless you copy that
  folder or apply the same settings.
- Touching particles that cannot be separated are counted as one.
- Inside a large halo or dense cluster only bright cores above ≈ 15 µm are recovered; smaller
  particles embedded in the halo are not detected, and very dense fields are still undercounted.
- Very faint particles (close to the background) fall below the colour threshold and are not
  candidates; lowering *Minimum brightness* on the Settings page helps but admits more noise.

---

## Español

App web local (Streamlit) para detectar y contar microplásticos en imágenes de microscopía de
fluorescencia. Motor **100 % local, gratis y sin conexión a internet**: procesamiento de imagen
clásico (OpenCV) por color, brillo, forma y nitidez de borde, con un clasificador liviano
(scikit-learn) que se calibra con tus propias fotos de referencia y correcciones. No usa ninguna IA
de terceros ni requiere API key.

### Instalación y ejecución

Requiere Python 3.11 o más nuevo (desarrollado en 3.13) y Git.

```bash
git clone https://github.com/EmiliaVillanueva/analizador-microplasticos.git
cd analizador-microplasticos
pip install -r requirements.txt
python -m streamlit run app.py
```

Se abre en `http://localhost:8501`. Usá `python -m streamlit` en vez de `streamlit` a secas: en
Windows suele dar "no se reconoce" porque la carpeta de scripts de pip no está en el PATH. El idioma
se elige en la barra lateral.

### Páginas

- **Principal**: subir imágenes (individuales o una carpeta), elegir tinción, analizar en lote con
  barra de progreso, borrar resultados y copiar una tabla a Excel.
- **Comparador**: original vs. imagen marcada, con tamaño de marcadores ajustable.
- **Entrenamiento**: subir fotos de referencia y marcar los microplásticos verdaderos.
- **Correcciones**: marcar falsos positivos/negativos de un análisis ya hecho.
- **Configuración**: rango de color (H/S/V) por tinción y recalibración del clasificador.

### Parámetros y reproducibilidad

Los parámetros por defecto están en la tabla de la sección en inglés. Solo los de
**Autofluorescencia (UV/azul)** fueron validados con muestras reales; los de Rodamina B, Rojo Nilo,
DAPI y "Otra" son puntos de partida. Los umbrales de área son fracciones del área de la imagen, así
que el tamaño mínimo en µm depende de la resolución y la calibración (µm/píxel) de tus fotos.

La carpeta `data/` (fotos de entrenamiento, correcciones, clasificadores y rangos de color que
cambies) **no se versiona**: una instalación nueva arranca con los valores por defecto y no repetirá
los resultados de una instalación calibrada localmente salvo que copies esa carpeta o repitas la
configuración. Las partículas que se tocan y no se pueden separar se cuentan como una.
