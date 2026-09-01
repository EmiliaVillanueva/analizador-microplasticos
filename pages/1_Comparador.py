"""Visor comparativo: original vs. imagen con detecciones marcadas, con tamaño de marcador ajustable."""
from __future__ import annotations

import io

import streamlit as st
from PIL import Image

from src import config, i18n, overlay

st.set_page_config(page_title="Comparador", page_icon="🔍", layout="wide")

i18n.language_selector()
t = i18n.t
lang = i18n.get_lang()

st.title(t("comp_title"))

resultados = st.session_state.get("resultados", [])

if not resultados:
    st.info(t("comp_no_results_info"))
    st.stop()

st.sidebar.subheader(t("comp_sidebar_header"))
radius_scale = st.sidebar.slider(
    t("comp_marker_size_label"), min_value=0.3, max_value=3.0, value=1.0, step=0.1,
    help=t("comp_marker_size_help"),
)
tipos_visibles = st.sidebar.multiselect(
    t("comp_types_label"),
    options=config.MORFOLOGIAS,
    default=config.MORFOLOGIAS,
    format_func=i18n.tipo_label,
)

nombres = [f"{i}: {r['filename']}" for i, r in enumerate(resultados) if not r["result"].error]
if not nombres:
    st.warning(t("comp_no_valid_warning"))
    st.stop()

seleccion = st.selectbox(t("comp_select_image_label"), nombres)
idx = int(seleccion.split(":")[0])
item = resultados[idx]
result = item["result"]

detecciones_filtradas = [d for d in result.detecciones if d.tipo in tipos_visibles]

col1, col2 = st.columns(2)
with col1:
    st.markdown(t("comp_original_label"))
    st.image(item["image_bytes"], width='stretch')
with col2:
    st.markdown(t("comp_marked_label"))
    img = Image.open(io.BytesIO(item["image_bytes"]))
    marcada = overlay.draw_detections(img, detecciones_filtradas, radius_scale=radius_scale)
    st.image(marcada, width='stretch')

st.divider()
st.markdown(t("comp_report_header"))
st.code(result.to_report_text(lang=lang), language=None)

st.markdown(t("comp_legend_header"))
leg_cols = st.columns(len(config.MORFOLOGIAS))
for col, tipo in zip(leg_cols, config.MORFOLOGIAS):
    col.markdown(
        f"<span style='color:{config.TIPO_COLORS[tipo]}'>●</span> {i18n.tipo_label(tipo)}",
        unsafe_allow_html=True,
    )
