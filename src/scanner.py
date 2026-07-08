"""
Orchestration du scan : pour chaque action de l'univers PEA, télécharge
l'historique, calcule les indicateurs, détecte les croisements, et construit
un tableau de résultats consolidé.
"""

import pandas as pd

from src import config
from src.data_fetcher import fetch_history
from src.indicators import (
    add_ema,
    detect_ema_crossover,
    add_rsi,
    add_volume_stats,
    add_range_stats,
    add_high_low_window,
    add_breakout_levels,
    detect_breakout,
    compute_trend_score,
)


def _safe_round(value, ndigits=3):
    """Retourne None si la valeur est NaN/absente (ex. historique trop court), sinon arrondit."""
    return None if pd.isna(value) else round(float(value), ndigits)


def scan_one_stock(stock: dict) -> dict | None:
    """Analyse une action et retourne une ligne de résultat, ou None si échec."""
    ticker = stock["ticker"]
    df = fetch_history(ticker, config.HISTORY_PERIOD, config.HISTORY_INTERVAL)

    # Minimum vital pour calculer les indicateurs de base (EMA9/20, RSI...).
    # L'EMA200, le 52 semaines, etc. peuvent rester incomplets (None) si
    # l'action est cotée depuis moins longtemps que la fenêtre demandée.
    if df is None or len(df) < config.EMA_LONG:
        return None

    df = add_ema(df, config.EMA_SHORT)
    df = add_ema(df, config.EMA_LONG)
    df = add_ema(df, config.EMA_TREND)
    df = add_rsi(df, config.RSI_PERIOD)
    df = add_volume_stats(df, config.VOLUME_AVG_PERIOD)
    df = add_range_stats(df, config.RANGE_PERIOD)
    df = add_high_low_window(df, config.HIGH_LOW_52W_WINDOW, "52s")
    df = add_high_low_window(df, config.BREAKOUT_PERIOD, "20j")
    df = add_breakout_levels(df, config.BREAKOUT_PERIOD)

    crossover = detect_ema_crossover(df, config.EMA_SHORT, config.EMA_LONG)
    cassure = detect_breakout(df, config.BREAKOUT_PERIOD)

    last = df.iloc[-1]
    prev_close = df.iloc[-2]["Close"] if len(df) >= 2 else last["Close"]
    variation_pct = ((last["Close"] - prev_close) / prev_close) * 100 if prev_close else 0.0

    ema9, ema20, ema200 = last[f"EMA_{config.EMA_SHORT}"], last[f"EMA_{config.EMA_LONG}"], last[f"EMA_{config.EMA_TREND}"]
    score_tendance, config_tendance = None, None
    if not (pd.isna(ema9) or pd.isna(ema20) or pd.isna(ema200)):
        score_tendance, config_tendance = compute_trend_score(last["Close"], ema9, ema20, ema200)

    volume_avg = last[f"volume_avg_{config.VOLUME_AVG_PERIOD}"]
    volume_ratio = (last["Volume"] / volume_avg) if volume_avg and not pd.isna(volume_avg) and volume_avg > 0 else None

    return {
        "ticker": ticker,
        "nom": stock["nom"],
        "secteur": stock["secteur"],
        "dernier_cours": round(float(last["Close"]), 2),
        "variation_jour_pct": round(float(variation_pct), 2),
        "volume": int(last["Volume"]) if not pd.isna(last["Volume"]) else None,
        f"volume_moyen_{config.VOLUME_AVG_PERIOD}j": _safe_round(volume_avg, 0),
        "volume_ratio": _safe_round(volume_ratio, 2),
        f"ema_{config.EMA_SHORT}": _safe_round(ema9),
        f"ema_{config.EMA_LONG}": _safe_round(ema20),
        f"ema_{config.EMA_TREND}": _safe_round(ema200),
        f"rsi_{config.RSI_PERIOD}": _safe_round(last[f"RSI_{config.RSI_PERIOD}"], 1),
        f"variation_moyenne_{config.RANGE_PERIOD}j_pct": _safe_round(last[f"range_avg_{config.RANGE_PERIOD}"], 2),
        "plus_haut_52s": _safe_round(last["high_52s"], 2),
        "plus_bas_52s": _safe_round(last["low_52s"], 2),
        "plus_haut_20j": _safe_round(last["high_20j"], 2),
        "plus_bas_20j": _safe_round(last["low_20j"], 2),
        "croisement": crossover,       # "haussier" / "baissier" / None
        "cassure_20j": cassure,        # "haussière" / "baissière" / None
        "score_tendance": score_tendance,
        "configuration_tendance": config_tendance,
        "date": last.name.strftime("%Y-%m-%d"),
    }


def run_scan(stocks: list[dict] | None = None) -> pd.DataFrame:
    """Exécute le scan complet sur l'univers d'actions et retourne un DataFrame."""
    stocks = stocks if stocks is not None else config.PEA_STOCKS
    results = []

    for stock in stocks:
        row = scan_one_stock(stock)
        if row is not None:
            results.append(row)
        else:
            print(f"[scanner] Ignoré (données indisponibles) : {stock['ticker']}")

    return pd.DataFrame(results)
