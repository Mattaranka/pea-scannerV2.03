"""
Scanner d'actions PEA - Page d'accueil.

Structure pensée pour être multi-pages (voir dossier pages/) : chaque nouvelle
fonctionnalité (RSI, Bollinger, alertes...) devient une page indépendante qui
réutilise les données produites par le job quotidien (data/scan_results.csv).
"""

import os
from datetime import datetime, timezone

import pandas as pd
import streamlit as st

from src import config

st.set_page_config(
    page_title="Scanner PEA",
    page_icon="📈",
    layout="wide",
)


@st.cache_data(ttl=300)
def load_data(mtime: float) -> pd.DataFrame:
    """Charge les résultats du scan. Le paramètre mtime invalide le cache
    Streamlit automatiquement dès que le fichier est mis à jour par le job
    GitHub Actions (pas besoin d'attendre l'expiration du TTL)."""
    return pd.read_csv(config.SCAN_RESULTS_FILE)


def get_last_update_str() -> str:
    if not os.path.exists(config.LAST_UPDATE_FILE):
        return "Jamais"
    with open(config.LAST_UPDATE_FILE) as f:
        ts = datetime.fromisoformat(f.read().strip())
    return ts.strftime("%d/%m/%Y à %H:%M UTC")


st.title("📈 Scanner d'actions éligibles au PEA")
st.caption("Univers : CAC 40 + principales valeurs SBF120 — mise à jour automatique chaque jour à 18h30")

if not os.path.exists(config.SCAN_RESULTS_FILE):
    st.warning(
        "Aucune donnée disponible pour le moment. Le premier scan sera exécuté "
        "à la prochaine mise à jour programmée, ou lance-le manuellement via "
        "l'onglet Actions de GitHub (workflow_dispatch)."
    )
    st.stop()

mtime = os.path.getmtime(config.SCAN_RESULTS_FILE)
df = load_data(mtime)

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Actions suivies", len(df))
col2.metric("Croisements EMA", int(df["croisement"].notna().sum()))
col3.metric("RSI en zone extrême", int(((df[f"rsi_{config.RSI_PERIOD}"] > config.RSI_OVERBOUGHT) |
                                          (df[f"rsi_{config.RSI_PERIOD}"] < config.RSI_OVERSOLD)).sum()))
col4.metric("Volumes anormaux", int((df["volume_ratio"] >= config.VOLUME_SPIKE_RATIO).sum()))
col5.metric("Dernière mise à jour", get_last_update_str())

st.divider()
st.subheader("Vue d'ensemble")

secteurs = ["Tous"] + sorted(df["secteur"].dropna().unique().tolist())
secteur_choisi = st.selectbox("Filtrer par secteur", secteurs)

df_affiche = df if secteur_choisi == "Tous" else df[df["secteur"] == secteur_choisi]

st.dataframe(
    df_affiche[[
        "ticker", "nom", "secteur", "dernier_cours", "variation_jour_pct",
        f"rsi_{config.RSI_PERIOD}", "score_tendance", "croisement", "cassure_20j",
    ]]
    .sort_values("nom")
    .rename(columns={
        "ticker": "Ticker",
        "nom": "Nom",
        "secteur": "Secteur",
        "dernier_cours": "Dernier cours (€)",
        "variation_jour_pct": "Variation jour (%)",
        f"rsi_{config.RSI_PERIOD}": f"RSI{config.RSI_PERIOD}",
        "score_tendance": "Score tendance",
        "croisement": "Croisement EMA9/20",
        "cassure_20j": "Cassure 20j",
    }),
    use_container_width=True,
    hide_index=True,
)

st.info(
    "👉 Le menu de gauche donne accès aux pages dédiées : **Croisements EMA**, "
    "**RSI** (survente/surachat), **Volumes** (volumes anormaux) et "
    "**Cassures** (cassure des plus haut/bas 20 jours)."
)
