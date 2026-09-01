"""Entrenamiento: subir fotos de referencia y marcar a mano los microplásticos verdaderos
(círculos ajustables de tamaño y posición) para calibrar el clasificador de esa tinción."""
from __future__ import annotations

import io

from PIL import Image

import streamlit as st
from src import config, feedback_store, i18n, overlay, training_store

st.set_page_config(page_title="Entrenamiento", page_icon="🎯", layout="wide")

i18n.language_selector()
t = i18n.t

st.title(t("train_title"))
st.caption(t("train_caption"))

MAX_DISPLAY_WIDTH = 700

tincion = st.selectbox(
    t("train_tincion_label"), config.TINCIONES, format_func=i18n.tincion_label, key="train_tincion"
)

uploaded = st.file_uploader(t("train_upload_label"), type=["jpg", "jpeg", "png", "bmp", "tif", "tiff"])

if uploaded:
    if st.session_state.get("train_last_file") != uploaded.name:
        st.session_state["train_pending_circles"] = []
        st.session_state["train_last_file"] = uploaded.name

    image_bytes = uploaded.getvalue()
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    scale = min(1.0, MAX_DISPLAY_WIDTH / img.width)
    disp_img = img.resize((int(img.width * scale), int(img.height * scale)))

    pendientes = st.session_state.setdefault("train_pending_circles", [])

    st.markdown(t("train_mark_instructions"))
    col_ctrl, col_prev = st.columns([1, 2])
    with col_ctrl:
        pos_x = st.slider(t("pos_x_label"), 0, 100, 50, key="train_pos_x")
        pos_y = st.slider(t("pos_y_label"), 0, 100, 50, key="train_pos_y")
        radio_pct = st.slider(t("radio_label"), 1, 30, 4, key="train_radio")
        if st.button(t("add_circle_button"), key="train_add_circle"):
            pendientes.append({"x": pos_x / 100, "y": pos_y / 100, "radio": radio_pct / 100})
            st.rerun()
        if pendientes and st.button(t("remove_last_button"), key="train_pop_circle"):
            pendientes.pop()
            st.rerun()

    with col_prev:
        preview = overlay.draw_manual_circles(disp_img, pendientes, color="#FFEB3B")
        preview = overlay.draw_manual_circles(
            preview, [{"x": pos_x / 100, "y": pos_y / 100, "radio": radio_pct / 100}], color="#00E5FF"
        )
        st.image(preview, width='stretch', caption=t("train_preview_caption"))

    st.write(t("circles_marked_label", n=len(pendientes)))

    nota = st.text_input(t("train_note_label"), placeholder=t("train_note_placeholder"))

    if st.button(t("save_example_button"), type="primary", disabled=not pendientes):
        ext = "." + (uploaded.name.rsplit(".", 1)[-1].lower() if "." in uploaded.name else "jpg")
        training_store.add_example(tincion, image_bytes, ext, pendientes, nota)
        st.session_state["train_pending_circles"] = []
        st.success(t("example_saved_success"))
        st.rerun()

st.divider()
st.subheader(t("saved_examples_header"))

filtro_tincion = st.selectbox(
    t("filter_tincion_label"),
    [t("filter_all_option")] + config.TINCIONES,
    format_func=lambda v: v if v == t("filter_all_option") else i18n.tincion_label(v),
    key="filtro_train",
)

if filtro_tincion != t("filter_all_option") and st.button(t("recalibrate_now_button", t=filtro_tincion)):
    resumen = feedback_store.retrain(filtro_tincion)
    if resumen["trained"]:
        if resumen["mode"] == "clasificador":
            st.success(t("trained_classifier_success", pos=resumen["n_pos"], neg=resumen["n_neg"]))
        else:
            st.success(t("adjusted_threshold_success", n=resumen["n_pos"] or resumen["n_neg"]))
    else:
        st.warning(feedback_store.explicar_insuficiente(resumen))
ejemplos = training_store.list_examples(
    None if filtro_tincion == t("filter_all_option") else filtro_tincion
)

if not ejemplos:
    st.info(t("no_examples_info"))
else:
    for ex in ejemplos:
        path = training_store.example_image_path(ex)
        if not path.exists():
            continue
        cols = st.columns([1, 2])
        with cols[0]:
            img = Image.open(path)
            marcada = overlay.draw_manual_circles(img, ex["circulos"])
            st.image(marcada, width='stretch')
        with cols[1]:
            st.markdown(f"{t('tincion_field_label')} {i18n.tincion_label(ex['tincion'])}")
            st.markdown(f"{t('circles_field_label')} {len(ex['circulos'])}")
            if ex.get("nota"):
                st.markdown(f"{t('note_field_label')} {ex['nota']}")
            st.caption(ex["fecha"])
            if st.button(t("delete_example_button"), key=f"del_{ex['id']}"):
                training_store.delete_example(ex["id"])
                st.rerun()
        st.divider()
