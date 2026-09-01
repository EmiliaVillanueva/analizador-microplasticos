"""Analizador de Microplásticos — página principal: analizar imágenes individuales o en lote."""
from __future__ import annotations

import io

import streamlit as st
from PIL import Image

from src import analyzer, config, i18n, overlay

st.set_page_config(page_title="Analizador de Microplásticos", page_icon="🔬", layout="wide")

i18n.language_selector()
t = i18n.t
lang = i18n.get_lang()

if "resultados" not in st.session_state:
    st.session_state["resultados"] = []  # lista de dict: {result, image_bytes, filename}

st.title(t("app_title"))
st.caption(t("app_subtitle"))

with st.sidebar:
    st.subheader(t("sidebar_config_header"))
    tincion = st.selectbox(
        t("sidebar_tincion_label"), config.TINCIONES, format_func=i18n.tincion_label
    )
    st.caption(t("sidebar_tincion_caption"))

st.subheader(t("section1_header"))

col1, col2 = st.columns(2)

with col1:
    st.markdown(t("upload_individual_header"))
    uploaded_files = st.file_uploader(
        t("upload_individual_label"),
        type=["jpg", "jpeg", "png", "bmp", "tif", "tiff"],
        accept_multiple_files=True,
    )

with col2:
    st.markdown(t("upload_folder_header"))
    folder_path = st.text_input(t("folder_path_label"), placeholder=r"C:\ruta\a\mis\fotos")
    folder_images = []
    if folder_path:
        folder_images = analyzer.list_images_in_folder(folder_path)
        if folder_images:
            st.info(t("folder_found_info", n=len(folder_images)))
        else:
            st.warning(t("folder_not_found_warning"))

items: list[tuple[str, bytes]] = []
if uploaded_files:
    for f in uploaded_files:
        items.append((f.name, f.getvalue()))
if folder_images:
    for p in folder_images:
        items.append((p.name, p.read_bytes()))

if items:
    st.caption(t("items_ready_caption", n=len(items)))

st.subheader(t("section2_header"))

analizar_btn = st.button(t("analyze_button"), type="primary", disabled=not items)

if analizar_btn:
    progress_bar = st.progress(0)
    status_text = st.empty()

    def _on_progress(done: int, total: int, filename: str) -> None:
        progress_bar.progress(done / total if total else 0)
        status_text.text(t("processing_status", done=done, total=total, filename=filename))

    resultados = analyzer.analyze_batch(
        items=items, tincion=tincion, on_progress=_on_progress, lang=lang
    )

    status_text.text(t("done_status", n=len(resultados)))

    nuevos = []
    for (filename, data), result in zip(items, resultados):
        nuevos.append({"result": result, "image_bytes": data, "filename": filename})
    st.session_state["resultados"] = nuevos + st.session_state["resultados"]

    fallidos = [r for r in resultados if r.error]
    if fallidos:
        st.error(t("failed_error", n=len(fallidos)))

st.subheader(t("section3_header"))

resultados_actuales = st.session_state["resultados"]
if not resultados_actuales:
    st.info(t("no_results_info"))
else:
    total_mp = sum(r["result"].conteo_total for r in resultados_actuales if not r["result"].error)
    st.metric(t("total_mp_metric"), total_mp)

    col_clear, col_table = st.columns(2)
    with col_clear:
        if st.button(t("clear_results_button")):
            st.session_state["resultados"] = []
            st.rerun()
    with col_table:
        mostrar_tabla = st.button(t("generate_table_button"))

    if mostrar_tabla:
        filas = [
            f"{item['filename']}\t{'ERROR' if item['result'].error else item['result'].conteo_total}"
            for item in resultados_actuales
        ]
        tabla_tsv = f"{t('table_header_archivo')}\t{t('table_header_mp')}\n" + "\n".join(filas)
        st.text_area(
            t("table_instructions"),
            value=tabla_tsv,
            height=min(35 + 28 * len(resultados_actuales), 400),
        )

    for item in resultados_actuales:
        result = item["result"]
        with st.expander(f"{item['filename']} — {'ERROR' if result.error else f'{result.conteo_total} MP'}"):
            if result.error:
                st.error(result.error)
                continue

            c1, c2 = st.columns(2)
            with c1:
                st.image(item["image_bytes"], caption=t("original_caption"), width='stretch')
            with c2:
                img = Image.open(io.BytesIO(item["image_bytes"]))
                marcada = overlay.draw_detections(img, result.detecciones)
                st.image(marcada, caption=t("detections_caption"), width='stretch')

            st.code(result.to_report_text(lang=lang), language=None)

st.divider()
st.caption(t("footer_caption"))
