"""
Page dédiée : actions dont le volume du jour dépasse un multiple du volume
moyen (détection d'un intérêt inhabituel du marché).
"""

import os

import pandas as pd
import streamlit as st

from src import config

st.set_page_config(page_title="Volumes - Scanner PEA", page_icon="📶", layout="wide")
st.title("📶 Volumes anormaux")
st.caption(f"Seuil : volume du jour ≥ {config.VOLUME_SPIKE_RATIO}× le volume moyen des "
           f"{config.VOLUME_AVG_PERIOD} jours précédents")

if not os.path.exists(config.SCAN_RESULTS_FILE):
    st.warning("Aucune donnée disponible pour le moment.")
    st.stop()


@st.cache_data(ttl=300)
def load_data(mtime: float) -> pd.DataFrame:
    return pd.read_csv(config.SCAN_RESULTS_FILE)


mtime = os.path.getmtime(config.SCAN_RESULTS_FILE)
df = load_data(mtime)

df_spike = df[df["volume_ratio"] >= config.VOLUME_SPIKE_RATIO].copy()

if df_spike.empty:
    st.success("Aucun volume anormal détecté aujourd'hui.")
    st.stop()

st.metric("Actions avec volume anormal", len(df_spike))
st.divider()

volume_avg_col = f"volume_moyen_{config.VOLUME_AVG_PERIOD}j"

st.dataframe(
    df_spike[["ticker", "nom", "secteur", "dernier_cours", "variation_jour_pct",
              "volume", volume_avg_col, "volume_ratio"]]
    .sort_values("volume_ratio", ascending=False)
    .rename(columns={
        "ticker": "Ticker",
        "nom": "Nom",
        "secteur": "Secteur",
        "dernier_cours": "Dernier cours (€)",
        "variation_jour_pct": "Variation jour (%)",
        "volume": "Volume du jour",
        volume_avg_col: f"Volume moyen ({config.VOLUME_AVG_PERIOD}j)",
        "volume_ratio": "Ratio (jour / moyen)",
    }),
    use_container_width=True,
    hide_index=True,
)
