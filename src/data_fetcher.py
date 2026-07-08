"""
Téléchargement des données de marché.

Isolé dans son propre module pour pouvoir remplacer yfinance par une autre
source (API broker, EOD Historical Data...) sans impacter le reste du code.
"""

import time
import pandas as pd
import yfinance as yf


def fetch_history(ticker: str, period: str, interval: str, retries: int = 3, pause: float = 2.0) -> pd.DataFrame | None:
    """
    Télécharge l'historique OHLCV d'un ticker, avec retry en cas d'erreur
    réseau ou de limitation de débit (fréquent avec yfinance en usage intensif).

    auto_adjust=False : on conserve les cours bruts (réellement cotés), pas
    les cours ajustés des dividendes. Les cours ajustés recalculent tout
    l'historique rétroactivement à chaque détachement de dividende, ce qui
    décale légèrement les EMA et peut faire apparaître un croisement avec
    plusieurs jours de décalage par rapport à ce qu'affiche un broker/une
    plateforme de trading (eToro, MetaTrader...) qui utilise les cours bruts.
    """
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            df = yf.Ticker(ticker).history(period=period, interval=interval, auto_adjust=False)
            if df is None or df.empty:
                last_error = "Données vides"
            else:
                return df
        except Exception as exc:  # noqa: BLE001 - on veut logguer puis réessayer
            last_error = str(exc)

        if attempt < retries:
            time.sleep(pause * attempt)  # backoff progressif

    print(f"[data_fetcher] Échec définitif pour {ticker}: {last_error}")
    return None
