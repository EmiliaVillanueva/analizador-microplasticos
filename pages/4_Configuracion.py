"""Configuración: rango de color por tinción y entrenamiento del clasificador."""
from __future__ import annotations

import streamlit as st

from src import classifier, config, feedback_store, hsv_profiles, i18n, training_store

st.set_page_config(page_title="Configuración", page_icon="⚙️", layout="wide")

i18n.language_selector()
t = i18n.t

st.title(t("config_title"))

st.subheader(t("color_range_header"))
st.caption(t("color_range_caption"))

tincion = st.selectbox(
    t("tincion_to_configure_label"), config.TINCIONES, format_func=i18n.tincion_label, key="cfg_tincion"
)
profile = hsv_profiles.get_profile(tincion)

hue_ranges = []
for i, (h_min, h_max) in enumerate(profile["hue_ranges"]):
    lo, hi = st.slider(
        t("hue_range_label", i=i + 1), min_value=0, max_value=179, value=(h_min, h_max), key=f"hue_{i}"
    )
    hue_ranges.append([lo, hi])

sat_min = st.slider(t("sat_min_label"), 0, 255, profile["sat_min"], key="sat_min")
val_min = st.slider(t("val_min_label"), 0, 255, profile["val_min"], key="val_min")

col_a, col_b = st.columns(2)
with col_a:
    if st.button(t("save_color_button")):
        hsv_profiles.set_profile(
            tincion, {"hue_ranges": hue_ranges, "sat_min": sat_min, "val_min": val_min}
        )
        st.success(t("saved_success"))
with col_b:
    if hsv_profiles.is_customized(tincion) and st.button(t("reset_defaults_button")):
        hsv_profiles.reset_profile(tincion)
        st.rerun()

st.divider()
st.subheader(t("classifier_header"))
st.caption(
    t(
        "classifier_caption",
        minimo=config.MIN_SAMPLES_PARA_ENTRENAR,
        sharpness=config.DEFAULT_SHARPNESS_MIN,
        solidity=config.DEFAULT_SOLIDITY_MIN,
    )
)

ESTADO_KEYS = {
    "clasificador": "state_clasificador",
    "umbral_ajustado": "state_umbral_ajustado",
    "por_defecto": "state_por_defecto",
}

for tc in config.TINCIONES:
    n_ejemplos = len(training_store.list_examples(tc))
    n_correcciones = len(feedback_store.list_corrections(tc))
    estado = classifier.status(tc)
    with st.expander(f"{i18n.tincion_label(tc)} — {t(ESTADO_KEYS[estado])}"):
        st.write(t("training_photos_count", n=n_ejemplos, n2=n_correcciones))
        cols = st.columns(2)
        with cols[0]:
            if st.button(t("recalibrate_button"), key=f"retrain_{tc}"):
                resumen = feedback_store.retrain(tc)
                if resumen["trained"]:
                    if resumen["mode"] == "clasificador":
                        st.success(t("trained_success2", pos=resumen["n_pos"], neg=resumen["n_neg"]))
                    else:
                        st.success(t("adjusted_success2", n=resumen["n_pos"] or resumen["n_neg"]))
                else:
                    st.warning(feedback_store.explicar_insuficiente(resumen))
        with cols[1]:
            if estado != "por_defecto" and st.button(t("revert_defaults_button"), key=f"forget_{tc}"):
                classifier.delete_model(tc)
                st.rerun()
