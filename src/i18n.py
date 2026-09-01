"""Sistema simple de traducción ES/EN para toda la app.

Los identificadores internos (nombres de tinción guardados en `config.TINCIONES`, tipos de
morfología) NO se traducen — son claves estables usadas para guardar/leer datos en disco
(perfiles de color, ejemplos de entrenamiento, correcciones). Solo se traduce lo que se le
muestra al usuario: para eso están `tincion_label()` y `tipo_label()`.
"""
from __future__ import annotations

import streamlit as st

from . import config

TRANSLATIONS: dict[str, dict[str, str]] = {
    "lang_label": {"es": "Idioma", "en": "Language"},

    # --- Página principal ---
    "app_title": {"es": "🔬 Analizador de Microplásticos", "en": "🔬 Microplastics Analyzer"},
    "app_subtitle": {
        "es": "Detección y conteo de microplásticos en imágenes de microscopía de fluorescencia. "
              "Motor 100% local (sin IA de terceros, sin costo, sin conexión a internet).",
        "en": "Detection and counting of microplastics in fluorescence microscopy images. "
              "100% local engine (no third-party AI, no cost, no internet connection).",
    },
    "sidebar_config_header": {"es": "Configuración", "en": "Settings"},
    "sidebar_tincion_label": {"es": "Tipo de tinción utilizada", "en": "Staining type used"},
    "sidebar_tincion_caption": {
        "es": "El rango de color esperado para cada tinción se ajusta en la página "
              "**Configuración**, junto con el entrenamiento del clasificador.",
        "en": "The expected color range for each staining is adjusted on the "
              "**Settings** page, along with classifier training.",
    },
    "section1_header": {"es": "1. Cargar imágenes", "en": "1. Load images"},
    "upload_individual_header": {
        "es": "**Imágenes individuales / selección múltiple**",
        "en": "**Individual images / multiple selection**",
    },
    "upload_individual_label": {"es": "Subí una o varias imágenes", "en": "Upload one or more images"},
    "upload_folder_header": {
        "es": "**Carpeta local (procesa todas las imágenes dentro)**",
        "en": "**Local folder (processes all images inside)**",
    },
    "folder_path_label": {"es": "Ruta de la carpeta", "en": "Folder path"},
    "folder_found_info": {
        "es": "Se encontraron {n} imágenes en la carpeta.",
        "en": "Found {n} images in the folder.",
    },
    "folder_not_found_warning": {
        "es": "No se encontraron imágenes en esa ruta (o la ruta no existe).",
        "en": "No images found at that path (or the path doesn't exist).",
    },
    "items_ready_caption": {
        "es": "{n} imagen(es) lista(s) para analizar.",
        "en": "{n} image(s) ready to analyze.",
    },
    "section2_header": {"es": "2. Analizar", "en": "2. Analyze"},
    "analyze_button": {"es": "Analizar imágenes", "en": "Analyze images"},
    "processing_status": {
        "es": "Procesando {done}/{total}: {filename}",
        "en": "Processing {done}/{total}: {filename}",
    },
    "done_status": {
        "es": "Listo: {n}/{n} imágenes procesadas.",
        "en": "Done: {n}/{n} images processed.",
    },
    "failed_error": {
        "es": "{n} imagen(es) fallaron y no interrumpieron el resto del lote.",
        "en": "{n} image(s) failed and did not interrupt the rest of the batch.",
    },
    "section3_header": {"es": "3. Resultados", "en": "3. Results"},
    "no_results_info": {
        "es": "Todavía no hay resultados. Cargá imágenes y presioná 'Analizar imágenes'.",
        "en": "No results yet. Load images and press 'Analyze images'.",
    },
    "total_mp_metric": {
        "es": "Total de microplásticos confirmados (todas las corridas)",
        "en": "Total confirmed microplastics (all runs)",
    },
    "clear_results_button": {"es": "🔄 Borrar todos los resultados", "en": "🔄 Clear all results"},
    "generate_table_button": {
        "es": "📋 Generar tabla para copiar a Excel", "en": "📋 Generate table to copy to Excel",
    },
    "table_instructions": {
        "es": "Seleccioná todo el texto (Ctrl+A) y copialo (Ctrl+C); al pegarlo en Excel "
              "(Ctrl+V) se acomoda solo en columnas.",
        "en": "Select all the text (Ctrl+A) and copy it (Ctrl+C); pasting it into Excel "
              "(Ctrl+V) will split it into columns automatically.",
    },
    "table_header_archivo": {"es": "Archivo", "en": "File"},
    "table_header_mp": {"es": "Microplasticos", "en": "Microplastics"},
    "original_caption": {"es": "Original", "en": "Original"},
    "detections_caption": {"es": "Detecciones marcadas", "en": "Marked detections"},
    "footer_caption": {
        "es": "Usá la página **Entrenamiento** para subir ejemplos marcados y **Correcciones** "
              "para enseñarle al programa a partir de sus errores. Los cambios se aplican "
              "después de recalibrar en **Configuración**.",
        "en": "Use the **Training** page to upload marked examples and **Corrections** to "
              "teach the program from its mistakes. Changes apply after recalibrating in "
              "**Settings**.",
    },

    # --- Reporte / resultado de análisis ---
    "report_total": {"es": "Conteo Total Confirmado", "en": "Confirmed Total Count"},
    "report_breakdown": {"es": "Desglose Morfológico", "en": "Morphological Breakdown"},
    "report_falsos_positivos": {"es": "Falsos Positivos Descartados", "en": "Discarded False Positives"},
    "discard_size": {
        "es": "{n} candidato(s) descartado(s) por tamaño fuera de rango",
        "en": "{n} candidate(s) discarded for out-of-range size",
    },
    "discard_classifier": {
        "es": "{n} candidato(s) descartado(s) por bordes difusos o forma irregular (posible "
              "desenfoque o autofluorescencia orgánica)",
        "en": "{n} candidate(s) discarded for blurry edges or irregular shape (possibly "
              "out-of-focus or organic autofluorescence)",
    },
    "discard_none": {
        "es": "No se descartó ningún candidato en esta imagen.",
        "en": "No candidates were discarded in this image.",
    },

    # --- Comparador ---
    "comp_title": {"es": "🔍 Visor comparativo", "en": "🔍 Comparison viewer"},
    "comp_no_results_info": {
        "es": "Todavía no hay resultados para comparar. Andá a la página principal y analizá "
              "imágenes primero.",
        "en": "No results to compare yet. Go to the main page and analyze images first.",
    },
    "comp_sidebar_header": {"es": "Ajustes de visualización", "en": "Display settings"},
    "comp_marker_size_label": {"es": "Tamaño de los marcadores", "en": "Marker size"},
    "comp_marker_size_help": {
        "es": "Agranda o achica los círculos de detección superpuestos (solo visual).",
        "en": "Enlarges or shrinks the overlaid detection circles (visual only).",
    },
    "comp_types_label": {"es": "Tipos a mostrar", "en": "Types to show"},
    "comp_no_valid_warning": {
        "es": "No hay resultados válidos (todos fallaron con error).",
        "en": "No valid results (all failed with an error).",
    },
    "comp_select_image_label": {"es": "Elegí una imagen analizada", "en": "Choose an analyzed image"},
    "comp_original_label": {"es": "**Original**", "en": "**Original**"},
    "comp_marked_label": {"es": "**Marcada**", "en": "**Marked**"},
    "comp_report_header": {"es": "### Reporte", "en": "### Report"},
    "comp_legend_header": {"es": "### Leyenda", "en": "### Legend"},

    # --- Entrenamiento ---
    "train_title": {"es": "🎯 Entrenamiento", "en": "🎯 Training"},
    "train_caption": {
        "es": "Subí una foto y marcá dónde están los microplásticos verdaderos (igual que en "
              "tus fotos de referencia con círculo amarillo sobre fondo negro). Estos ejemplos "
              "calibran el clasificador de esa tinción — después de guardar varios, recalibrá "
              "acá abajo o en Configuración.",
        "en": "Upload a photo and mark where the real microplastics are (just like your "
              "reference photos with a yellow circle on a black background). These examples "
              "calibrate the classifier for that staining — after saving a few, recalibrate "
              "below or on the Settings page.",
    },
    "train_tincion_label": {
        "es": "Tinción de esta foto de referencia", "en": "Staining of this reference photo",
    },
    "train_upload_label": {"es": "Imagen de referencia", "en": "Reference image"},
    "train_mark_instructions": {
        "es": "**Marcar un microplástico:** ubicalo con los controles y presioná "
              "'Agregar círculo'.",
        "en": "**Mark a microplastic:** locate it with the controls and press 'Add circle'.",
    },
    "pos_x_label": {"es": "Posición horizontal (%)", "en": "Horizontal position (%)"},
    "pos_y_label": {"es": "Posición vertical (%)", "en": "Vertical position (%)"},
    "radio_label": {
        "es": "Tamaño del círculo (radio, % del ancho)", "en": "Circle size (radius, % of width)",
    },
    "add_circle_button": {"es": "➕ Agregar círculo", "en": "➕ Add circle"},
    "remove_last_button": {"es": "Quitar el último", "en": "Remove last"},
    "train_preview_caption": {
        "es": "Amarillo: ya agregados. Celeste: el que estás ubicando.",
        "en": "Yellow: already added. Cyan: the one you're placing.",
    },
    "circles_marked_label": {"es": "Círculos marcados: {n}", "en": "Circles marked: {n}"},
    "train_note_label": {
        "es": "Nota opcional sobre este ejemplo", "en": "Optional note about this example",
    },
    "train_note_placeholder": {
        "es": "Ej: fibras finas cerca de aglomerados orgánicos que NO deben confundirse",
        "en": "E.g.: thin fibers near organic clumps that should NOT be confused with MPs",
    },
    "save_example_button": {
        "es": "Guardar como ejemplo de entrenamiento", "en": "Save as training example",
    },
    "example_saved_success": {"es": "Ejemplo guardado.", "en": "Example saved."},
    "saved_examples_header": {"es": "Ejemplos guardados", "en": "Saved examples"},
    "filter_tincion_label": {"es": "Filtrar por tinción", "en": "Filter by staining"},
    "filter_all_option": {"es": "Todas", "en": "All"},
    "recalibrate_now_button": {"es": "Recalibrar '{t}' ahora", "en": "Recalibrate '{t}' now"},
    "trained_classifier_success": {
        "es": "Clasificador entrenado con {pos} positivos y {neg} negativos.",
        "en": "Classifier trained with {pos} positives and {neg} negatives.",
    },
    "adjusted_threshold_success": {
        "es": "Umbral ajustado con {n} ejemplo(s) de una sola clase (todavía no alcanza para un "
              "clasificador completo).",
        "en": "Threshold adjusted with {n} single-class example(s) (not enough yet for a full "
              "classifier).",
    },
    "insufficient_warning": {
        "es": "Hay {pos} positivos y {neg} negativos ({total} en total), pero el mínimo es "
              "{minimo}. Sumá más ejemplos en Entrenamiento o Correcciones.",
        "en": "There are {pos} positives and {neg} negatives ({total} total), but the minimum "
              "is {minimo}. Add more examples in Training or Corrections.",
    },
    "no_examples_info": {
        "es": "Todavía no hay ejemplos guardados para este filtro.",
        "en": "No saved examples yet for this filter.",
    },
    "tincion_field_label": {"es": "**Tinción:**", "en": "**Staining:**"},
    "circles_field_label": {"es": "**Círculos:**", "en": "**Circles:**"},
    "note_field_label": {"es": "**Nota:**", "en": "**Note:**"},
    "delete_example_button": {"es": "Eliminar ejemplo", "en": "Delete example"},

    # --- Correcciones ---
    "corr_title": {"es": "✏️ Correcciones", "en": "✏️ Corrections"},
    "corr_caption": {
        "es": "Marcá los errores del análisis: detecciones que NO eran microplásticos, o "
              "microplásticos que no se detectaron. Cada corrección se suma a los ejemplos de "
              "Entrenamiento para recalibrar el clasificador en la página Configuración.",
        "en": "Mark the analysis errors: detections that were NOT microplastics, or "
              "microplastics that weren't detected. Each correction adds to the Training "
              "examples to recalibrate the classifier on the Settings page.",
    },
    "corr_no_results_info": {
        "es": "Todavía no hay resultados para corregir. Andá a la página principal y analizá "
              "imágenes primero.",
        "en": "No results to correct yet. Go to the main page and analyze images first.",
    },
    "tab_fp_label": {
        "es": "Falsos positivos (detecciones incorrectas)",
        "en": "False positives (incorrect detections)",
    },
    "tab_fn_label": {
        "es": "Falsos negativos (MP no detectados)", "en": "False negatives (undetected MPs)",
    },
    "no_detections_info": {
        "es": "Esta imagen no tiene detecciones para revisar.",
        "en": "This image has no detections to review.",
    },
    "fp_instructions": {
        "es": "Elegí una detección de la lista y confirmá si NO era un microplástico real.",
        "en": "Choose a detection from the list and confirm whether it was NOT a real "
              "microplastic.",
    },
    "current_detections_caption": {"es": "Detecciones actuales", "en": "Current detections"},
    "detection_option_label": {"es": "Detección a revisar", "en": "Detection to review"},
    "crop_caption": {"es": "Recorte de la detección", "en": "Detection crop"},
    "mark_fp_button": {
        "es": "Marcar como FALSO POSITIVO (no era un MP)",
        "en": "Mark as FALSE POSITIVE (not an MP)",
    },
    "fp_saved_success": {
        "es": "Guardado como ejemplo negativo. Recalibrá en Configuración para aplicarlo.",
        "en": "Saved as a negative example. Recalibrate in Settings to apply it.",
    },
    "fn_instructions": {
        "es": "Ubicá con los controles un microplástico real que el programa NO haya marcado y "
              "presioná 'Agregar círculo'. Podés agregar varios antes de guardar.",
        "en": "Use the controls to locate a real microplastic the program did NOT mark, and "
              "press 'Add circle'. You can add several before saving.",
    },
    "fn_preview_caption": {
        "es": "Verde: falsos negativos a guardar. Blanco: el que estás ubicando.",
        "en": "Green: false negatives to save. White: the one you're placing.",
    },
    "new_circles_label": {"es": "Círculos nuevos: {n}", "en": "New circles: {n}"},
    "save_fn_button": {
        "es": "Guardar como FALSOS NEGATIVOS (faltó marcarlos)",
        "en": "Save as FALSE NEGATIVES (they were missed)",
    },
    "fn_saved_msg": {
        "es": "{n} ejemplo(s) positivo(s) guardado(s). Recalibrá en Configuración.",
        "en": "{n} positive example(s) saved. Recalibrate in Settings.",
    },
    "fn_warning_approx": {
        "es": "\n\n⚠️ {n} de ellos NO fueron detectados por el rango de color configurado para "
              "esta tinción (son muy parecidos al fondo) — se guardaron con una aproximación "
              "menos confiable. Recalibrar el clasificador con estos NO va a ayudar mucho: "
              "probá primero bajar 'Saturación mínima' y/o 'Brillo mínimo (V)' en Configuración "
              "para esta tinción, así el motor los detecta como candidatos antes de intentar "
              "clasificarlos.",
        "en": "\n\n⚠️ {n} of them were NOT detected by the color range configured for this "
              "staining (they're very similar to the background) — they were saved using a "
              "less reliable approximation. Recalibrating the classifier with these won't help "
              "much: try lowering 'Minimum saturation' and/or 'Minimum brightness (V)' in "
              "Settings for this staining first, so the engine detects them as candidates "
              "before trying to classify them.",
    },
    "saved_corrections_header": {"es": "Correcciones guardadas", "en": "Saved corrections"},
    "label_missed": {"es": "Faltó marcar (falso negativo)", "en": "Missed (false negative)"},
    "label_wrong": {"es": "No era un MP (falso positivo)", "en": "Not an MP (false positive)"},
    "image_field_label": {"es": "Imagen: {n}", "en": "Image: {n}"},
    "delete_button": {"es": "Eliminar", "en": "Delete"},
    "no_corrections_info": {
        "es": "Todavía no hay correcciones guardadas para este filtro.",
        "en": "No saved corrections yet for this filter.",
    },

    # --- Configuración ---
    "config_title": {"es": "⚙️ Configuración", "en": "⚙️ Settings"},
    "color_range_header": {"es": "Rango de color por tinción", "en": "Color range by staining"},
    "color_range_caption": {
        "es": "Define qué color/brillo cuenta como señal para cada tinción. Los valores por "
              "defecto son un punto de partida razonable; ajustalos si el motor no detecta "
              "bien el color de tus fotos.",
        "en": "Defines what color/brightness counts as signal for each staining. The default "
              "values are a reasonable starting point; adjust them if the engine doesn't "
              "detect your photos' color well.",
    },
    "tincion_to_configure_label": {"es": "Tinción a configurar", "en": "Staining to configure"},
    "hue_range_label": {"es": "Rango de tono (H) #{i}", "en": "Hue range (H) #{i}"},
    "sat_min_label": {"es": "Saturación mínima", "en": "Minimum saturation"},
    "val_min_label": {"es": "Brillo mínimo (V)", "en": "Minimum brightness (V)"},
    "save_color_button": {"es": "Guardar rango de color", "en": "Save color range"},
    "saved_success": {"es": "Guardado.", "en": "Saved."},
    "reset_defaults_button": {
        "es": "Restablecer valores por defecto", "en": "Reset to default values",
    },
    "classifier_header": {
        "es": "Clasificador entrenable (MP real vs. artefacto)",
        "en": "Trainable classifier (real MP vs. artifact)",
    },
    "classifier_caption": {
        "es": "Combina los ejemplos de Entrenamiento (círculos amarillos) y de Correcciones "
              "para calibrar la detección por tinción. Con al menos {minimo} ejemplos entrena "
              "un clasificador (si hay de ambas clases) o ajusta el umbral por defecto (si son "
              "todos de una clase). Sin ejemplos suficientes usa los umbrales por defecto "
              "(nitidez de borde ≥ {sharpness}, solidez de forma ≥ {solidity}).",
        "en": "Combines Training examples (yellow circles) and Corrections to calibrate "
              "detection per staining. With at least {minimo} examples it trains a classifier "
              "(if both classes are present) or adjusts the default threshold (if all examples "
              "are one class). Without enough examples it uses the default thresholds (edge "
              "sharpness ≥ {sharpness}, shape solidity ≥ {solidity}).",
    },
    "state_clasificador": {"es": "clasificador entrenado", "en": "trained classifier"},
    "state_umbral_ajustado": {
        "es": "umbral ajustado con tus ejemplos", "en": "threshold adjusted with your examples",
    },
    "state_por_defecto": {
        "es": "usando umbrales por defecto", "en": "using default thresholds",
    },
    "training_photos_count": {
        "es": "Fotos de entrenamiento: {n} · Correcciones: {n2}",
        "en": "Training photos: {n} · Corrections: {n2}",
    },
    "recalibrate_button": {"es": "Recalibrar", "en": "Recalibrate"},
    "trained_success2": {
        "es": "Entrenado con {pos} positivos y {neg} negativos.",
        "en": "Trained with {pos} positives and {neg} negatives.",
    },
    "adjusted_success2": {
        "es": "Ajustado el umbral con {n} ejemplo(s) de una sola clase (no alcanza para un "
              "clasificador completo, pero ya corrige la detección en esa dirección).",
        "en": "Threshold adjusted with {n} single-class example(s) (not enough for a full "
              "classifier, but it already nudges detection in that direction).",
    },
    "revert_defaults_button": {
        "es": "Volver a umbrales por defecto", "en": "Revert to default thresholds",
    },
}

TINCION_LABELS_EN: dict[str, str] = {
    "Autofluorescencia (UV/azul)": "Autofluorescence (UV/blue)",
    "Rodamina B": "Rhodamine B",
    "Rojo Nilo (Nile Red)": "Nile Red",
    "DAPI": "DAPI",
    "Otra / personalizada": "Other / custom",
}

TIPO_LABELS_EN: dict[str, str] = {
    "fibra": "Fibers",
    "fragmento": "Fragments",
    "pelicula_esfera": "Films/Spheres",
}


def get_lang() -> str:
    return st.session_state.get("lang", "es")


def t(key: str, lang: str | None = None, **kwargs) -> str:
    entry = TRANSLATIONS.get(key)
    if entry is None:
        return key
    text = entry.get(lang or get_lang(), entry.get("es", key))
    return text.format(**kwargs) if kwargs else text


def tincion_label(value: str) -> str:
    """Etiqueta traducida para mostrar una tinción; el valor guardado/usado internamente
    (config.TINCIONES) no cambia, solo lo que se le muestra al usuario."""
    if get_lang() == "en":
        return TINCION_LABELS_EN.get(value, value)
    return value


def tipo_label(tipo: str) -> str:
    """Etiqueta traducida para un tipo de morfología (fibra/fragmento/pelicula_esfera)."""
    if get_lang() == "en":
        return TIPO_LABELS_EN.get(tipo, tipo)
    return config.TIPO_LABELS.get(tipo, tipo)


def language_selector() -> None:
    """El widget en sí (key="lang_widget") pierde su estado al navegar entre páginas de la app
    multipágina de Streamlit, así que el idioma persistido vive en st.session_state["lang"]
    (un valor plano, no atado a ningún widget) y se lo pasamos al selector como `index` en cada
    corrida — si el usuario elige otro valor en esta corrida, lo sincronizamos y reejecutamos."""
    if "lang" not in st.session_state:
        st.session_state["lang"] = "es"
    labels = {"es": "Español", "en": "English"}
    options = ["es", "en"]
    actual = st.session_state["lang"]
    elegido = st.sidebar.selectbox(
        t("lang_label"),
        options=options,
        index=options.index(actual),
        format_func=lambda o: labels[o],
        key="lang_widget",
    )
    if elegido != actual:
        st.session_state["lang"] = elegido
        st.rerun()
