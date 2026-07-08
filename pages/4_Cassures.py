"""
Page dédiée : actions ayant cassé leur plus haut ou leur plus bas des
20 jours précédents lors de la dernière session.
"""

import os

import pandas as pd
import streamlit as st

from src import config

st.set_page_config(page_title="Cassures - Scanner PEA", page_icon="🚀", layout="wide")
st.title("🚀 Cassures 20 jours")
st.caption("Actions dont le cours de clôture a dépassé le plus haut, ou est passé sous le plus bas, "
           "des 20 séances précédentes")

if not os.path.exists(config.SCAN_RESULTS_FILE):
    st.warning("Aucune donnée disponible pour le moment.")
    st.stop()


@st.cache_data(ttl=300)
def load_data(mtime: float) -> pd.DataFrame:
    return pd.read_csv(config.SCAN_RESULTS_FILE)


mtime = os.path.getmtime(config.SCAN_RESULTS_FILE)
df = load_data(mtime)

df_cassures = df[df["cassure_20j"].notna()].copy()

if df_cassures.empty:
    st.success("Aucune cassure détectée lors de la dernière session.")
    st.stop()

col1, col2 = st.columns(2)
col1.metric("Cassures haussières 🟢", int((df_cassures["cassure_20j"] == "haussière").sum()))
col2.metric("Cassures baissières 🔴", int((df_cassures["cassure_20j"] == "baissière").sum()))

st.divider()

type_choisi = st.radio(
    "Type de cassure",
    options=["Tous", "haussière", "baissière"],
    horizontal=True,
    format_func=lambda x: {"Tous": "Tous", "haussière": "🟢 Haussières", "baissière": "🔴 Baissières"}[x],
)

df_filtre = df_cassures if type_choisi == "Tous" else df_cassures[df_cassures["cassure_20j"] == type_choisi]

st.dataframe(
    df_filtre[["ticker", "nom", "secteur", "dernier_cours", "variation_jour_pct",
               "plus_haut_20j", "plus_bas_20j", "cassure_20j"]]
    .sort_values("nom")
    .rename(columns={
        "ticker": "Ticker",
        "nom": "Nom",
        "secteur": "Secteur",
        "dernier_cours": "Dernier cours (€)",
        "variation_jour_pct": "Variation jour (%)",
        "plus_haut_20j": "Plus haut 20j (€)",
        "plus_bas_20j": "Plus bas 20j (€)",
        "cassure_20j": "Cassure",
    }),
    use_container_width=True,
    hide_index=True,
)
