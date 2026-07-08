"""
Page dédiée : liste des actions dont l'EMA9 et l'EMA20 se sont croisées
lors de la dernière session boursière.
"""

import os

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

from src import config

st.set_page_config(page_title="Croisements EMA - Scanner PEA", page_icon="📈", layout="wide")
st.title("🔀 Croisements EMA9 / EMA20 du jour")

if not os.path.exists(config.SCAN_RESULTS_FILE):
    st.warning("Aucune donnée disponible pour le moment.")
    st.stop()


@st.cache_data(ttl=300)
def load_data(mtime: float) -> pd.DataFrame:
    return pd.read_csv(config.SCAN_RESULTS_FILE)


mtime = os.path.getmtime(config.SCAN_RESULTS_FILE)
df = load_data(mtime)

df_croisements = df[df["croisement"].notna()].copy()

if df_croisements.empty:
    st.success("Aucun croisement EMA9/EMA20 détecté lors de la dernière session.")
    st.stop()

col1, col2 = st.columns(2)
col1.metric("Croisements haussiers 🟢", int((df_croisements["croisement"] == "haussier").sum()))
col2.metric("Croisements baissiers 🔴", int((df_croisements["croisement"] == "baissier").sum()))

st.divider()

type_choisi = st.radio(
    "Type de croisement",
    options=["Tous", "haussier", "baissier"],
    horizontal=True,
    format_func=lambda x: {"Tous": "Tous", "haussier": "🟢 Haussiers", "baissier": "🔴 Baissiers"}[x],
)

df_filtre = df_croisements if type_choisi == "Tous" else df_croisements[df_croisements["croisement"] == type_choisi]

st.dataframe(
    df_filtre[[
        "ticker", "nom", "secteur", "dernier_cours", "variation_jour_pct",
        f"ema_{config.EMA_SHORT}", f"ema_{config.EMA_LONG}", "croisement", "date",
    ]].rename(columns={
        "ticker": "Ticker",
        "nom": "Nom",
        "secteur": "Secteur",
        "dernier_cours": "Dernier cours (€)",
        "variation_jour_pct": "Variation jour (%)",
        f"ema_{config.EMA_SHORT}": f"EMA{config.EMA_SHORT}",
        f"ema_{config.EMA_LONG}": f"EMA{config.EMA_LONG}",
        "croisement": "Type de croisement",
        "date": "Date de la session",
    }),
    use_container_width=True,
    hide_index=True,
)

st.divider()
st.subheader("Visualiser un croisement")

ticker_choisi = st.selectbox("Choisir une action pour afficher son graphique", df_filtre["ticker"].tolist())

if ticker_choisi:
    hist = yf.Ticker(ticker_choisi).history(period=config.HISTORY_PERIOD, interval=config.HISTORY_INTERVAL, auto_adjust=False)
    hist[f"EMA_{config.EMA_SHORT}"] = hist["Close"].ewm(span=config.EMA_SHORT, adjust=False).mean()
    hist[f"EMA_{config.EMA_LONG}"] = hist["Close"].ewm(span=config.EMA_LONG, adjust=False).mean()

    # Les EMA sont calculées sur l'historique complet (2 ans, nécessaire pour
    # leur stabilisation) mais on n'affiche que les 6 derniers mois pour que
    # le graphique reste lisible.
    hist_affiche = hist.tail(130)

    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=hist_affiche.index, open=hist_affiche["Open"], high=hist_affiche["High"],
        low=hist_affiche["Low"], close=hist_affiche["Close"],
        name="Cours",
    ))
    fig.add_trace(go.Scatter(x=hist_affiche.index, y=hist_affiche[f"EMA_{config.EMA_SHORT}"],
                              name=f"EMA{config.EMA_SHORT}", line=dict(color="orange", width=1.5)))
    fig.add_trace(go.Scatter(x=hist_affiche.index, y=hist_affiche[f"EMA_{config.EMA_LONG}"],
                              name=f"EMA{config.EMA_LONG}", line=dict(color="blue", width=1.5)))
    fig.update_layout(
        title=f"{ticker_choisi} — Cours et EMA{config.EMA_SHORT}/{config.EMA_LONG}",
        xaxis_rangeslider_visible=False,
        height=550,
    )
    st.plotly_chart(fig, use_container_width=True)
