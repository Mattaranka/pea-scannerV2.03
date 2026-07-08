"""
Page dédiée : actions dont le RSI14 est en zone de surachat (>70) ou de
survente (<30).
"""

import os

import pandas as pd
import streamlit as st

from src import config

st.set_page_config(page_title="RSI - Scanner PEA", page_icon="📊", layout="wide")
st.title("📊 RSI — Zones de surachat / survente")
st.caption(f"Seuils : surachat > {config.RSI_OVERBOUGHT}, survente < {config.RSI_OVERSOLD}")

if not os.path.exists(config.SCAN_RESULTS_FILE):
    st.warning("Aucune donnée disponible pour le moment.")
    st.stop()


@st.cache_data(ttl=300)
def load_data(mtime: float) -> pd.DataFrame:
    return pd.read_csv(config.SCAN_RESULTS_FILE)


mtime = os.path.getmtime(config.SCAN_RESULTS_FILE)
df = load_data(mtime)

rsi_col = f"rsi_{config.RSI_PERIOD}"
df_extreme = df[(df[rsi_col] > config.RSI_OVERBOUGHT) | (df[rsi_col] < config.RSI_OVERSOLD)].copy()

if df_extreme.empty:
    st.success("Aucune action en zone de surachat ou de survente aujourd'hui.")
    st.stop()

col1, col2 = st.columns(2)
col1.metric("Surachat (RSI > 70) 🔴", int((df_extreme[rsi_col] > config.RSI_OVERBOUGHT).sum()))
col2.metric("Survente (RSI < 30) 🟢", int((df_extreme[rsi_col] < config.RSI_OVERSOLD).sum()))

st.divider()

type_choisi = st.radio(
    "Filtrer",
    options=["Tous", "surachat", "survente"],
    horizontal=True,
    format_func=lambda x: {"Tous": "Tous", "surachat": "🔴 Surachat (>70)", "survente": "🟢 Survente (<30)"}[x],
)

if type_choisi == "surachat":
    df_filtre = df_extreme[df_extreme[rsi_col] > config.RSI_OVERBOUGHT]
elif type_choisi == "survente":
    df_filtre = df_extreme[df_extreme[rsi_col] < config.RSI_OVERSOLD]
else:
    df_filtre = df_extreme

st.dataframe(
    df_filtre[["ticker", "nom", "secteur", "dernier_cours", "variation_jour_pct", rsi_col]]
    .sort_values(rsi_col, ascending=False)
    .rename(columns={
        "ticker": "Ticker",
        "nom": "Nom",
        "secteur": "Secteur",
        "dernier_cours": "Dernier cours (€)",
        "variation_jour_pct": "Variation jour (%)",
        rsi_col: f"RSI{config.RSI_PERIOD}",
    }),
    use_container_width=True,
    hide_index=True,
)
