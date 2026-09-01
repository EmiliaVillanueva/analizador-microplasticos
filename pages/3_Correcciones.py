"""Correcciones: decile al programa cuándo se equivocó. Cada corrección queda guardada como
ejemplo positivo/negativo para recalibrar el clasificador de esa tinción."""
from __future__ import annotations

import io

from PIL import Image

import streamlit as st
from src import config, cv_engine, feedback_store, hsv_profiles, i18n, overlay

st.set_page_config(page_title="Correcciones", page_icon="✏️", layout="wide")

i18n.language_selector()
t = i18n.t

st.title(t("corr_title"))
st.caption(t("corr_caption"))

resultados = st.session_state.get("resultados", [])

if not resultados:
    st.info(t("corr_no_results_info"))
    st.stop()

nombres = [f"{i}: {r['filename']}" for i, r in enumerate(resultados) if not r["result"].error]
if not nombres:
    st.warning(t("comp_no_valid_warning"))
    st.stop()

seleccion = st.selectbox(t("comp_select_image_label"), nombres)
idx = int(seleccion.split(":")[0])
item = resultados[idx]
result = item["result"]
img_pil = Image.open(io.BytesIO(item["image_bytes"])).convert("RGB")

if st.session_state.get("corr_last_idx") != idx:
    st.session_state["corr_pending_circles"] = []
    st.session_state["corr_last_idx"] = idx

tab_fp, tab_fn = st.tabs([t("tab_fp_label"), t("tab_fn_label")])

with tab_fp:
    if not result.detecciones:
        st.info(t("no_detections_info"))
    else:
        st.caption(t("fp_instructions"))
        marcada = overlay.draw_detections(img_pil, result.detecciones)
        st.image(marcada, width='stretch', caption=t("current_detections_caption"))

        opciones = [
            f"#{i} — {i18n.tipo_label(d.tipo)} ({d.confianza:.0%})"
            for i, d in enumerate(result.detecciones)
        ]
        sel = st.selectbox(t("detection_option_label"), opciones, key="fp_select")
        det_idx = int(sel.split("—")[0].strip().lstrip("#"))
        det = result.detecciones[det_idx]

        w, h = img_pil.size
        r_px = max(det.radio * w, 8)
        cx_px, cy_px = det.x * w, det.y * h
        crop = img_pil.crop((
            max(0, cx_px - r_px * 2), max(0, cy_px - r_px * 2),
            min(w, cx_px + r_px * 2), min(h, cy_px + r_px * 2),
        ))
        cc1, cc2 = st.columns([1, 3])
        with cc1:
            st.image(crop, caption=t("crop_caption"))
        with cc2:
            if st.button(t("mark_fp_button"), key="btn_fp"):
                feedback_store.add_correction(
                    result.tincion, det.features, label=0, imagen_nombre=item["filename"]
                )
                st.success(t("fp_saved_success"))

with tab_fn:
    MAX_DISPLAY_WIDTH = 700
    scale = min(1.0, MAX_DISPLAY_WIDTH / img_pil.width)
    disp_img = img_pil.resize((int(img_pil.width * scale), int(img_pil.height * scale)))
    pendientes = st.session_state.setdefault("corr_pending_circles", [])

    st.caption(t("fn_instructions"))
    col_ctrl, col_prev = st.columns([1, 2])
    with col_ctrl:
        pos_x = st.slider(t("pos_x_label"), 0, 100, 50, key="corr_pos_x")
        pos_y = st.slider(t("pos_y_label"), 0, 100, 50, key="corr_pos_y")
        radio_pct = st.slider(t("radio_label"), 1, 30, 4, key="corr_radio")
        if st.button(t("add_circle_button"), key="corr_add_circle"):
            pendientes.append({"x": pos_x / 100, "y": pos_y / 100, "radio": radio_pct / 100})
            st.rerun()
        if pendientes and st.button(t("remove_last_button"), key="corr_pop_circle"):
            pendientes.pop()
            st.rerun()

    with col_prev:
        preview = overlay.draw_detections(disp_img, result.detecciones)
        preview = overlay.draw_manual_circles(preview, pendientes, color="#00E676")
        preview = overlay.draw_manual_circles(
            preview, [{"x": pos_x / 100, "y": pos_y / 100, "radio": radio_pct / 100}], color="#FFFFFF"
        )
        st.image(preview, width='stretch', caption=t("fn_preview_caption"))

    st.write(t("new_circles_label", n=len(pendientes)))

    if "corr_flash" in st.session_state:
        nivel, texto = st.session_state.pop("corr_flash")
        getattr(st, nivel)(texto)

    if st.button(t("save_fn_button"), disabled=not pendientes):
        img_bgr = cv_engine.decode_image(item["image_bytes"])
        profile = hsv_profiles.get_profile(result.tincion)
        n_aproximados = 0
        for c in pendientes:
            features = cv_engine.features_for_region(img_bgr, c["x"], c["y"], c["radio"], profile)
            if features.get("metodo") == "circulo_aproximado":
                n_aproximados += 1
            feedback_store.add_correction(result.tincion, features, label=1, imagen_nombre=item["filename"])
        st.session_state["corr_pending_circles"] = []

        mensaje = t("fn_saved_msg", n=len(pendientes))
        if n_aproximados:
            mensaje += t("fn_warning_approx", n=n_aproximados)
            st.session_state["corr_flash"] = ("warning", mensaje)
        else:
            st.session_state["corr_flash"] = ("success", mensaje)
        st.rerun()

st.divider()
st.subheader(t("saved_corrections_header"))
filtro = st.selectbox(
    t("filter_tincion_label"),
    [t("filter_all_option")] + config.TINCIONES,
    format_func=lambda v: v if v == t("filter_all_option") else i18n.tincion_label(v),
    key="filtro_corr",
)
correcciones = feedback_store.list_corrections(None if filtro == t("filter_all_option") else filtro)

if not correcciones:
    st.info(t("no_corrections_info"))
else:
    for c in correcciones:
        with st.container(border=True):
            etiqueta = t("label_missed") if c["label"] == 1 else t("label_wrong")
            st.markdown(f"**{i18n.tincion_label(c['tincion'])}** · {etiqueta} · _{c['fecha']}_")
            if c.get("imagen_nombre"):
                st.caption(t("image_field_label", n=c["imagen_nombre"]))
            if st.button(t("delete_button"), key=f"del_corr_{c['id']}"):
                feedback_store.delete_correction(c["id"])
                st.rerun()
