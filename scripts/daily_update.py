"""
Point d'entrée du job quotidien (déclenché par GitHub Actions à 18h30).

Lance le scan complet, sauvegarde les résultats en CSV, et écrit un
horodatage lisible pour l'affichage dans l'application Streamlit.
"""

import os
import sys
from datetime import datetime, timezone

# Permet d'exécuter ce script directement (python scripts/daily_update.py)
# en trouvant le package src/ à la racine du projet.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import config
from src.scanner import run_scan


def archive_scan(df, scan_date: str) -> str:
    """
    Sauvegarde une copie horodatée du scan dans data/history/AAAA-MM-JJ.csv.

    Cette archive est la brique de base du futur backtesting : elle permet de
    reconstituer, jour après jour, l'état exact des indicateurs au moment du
    scan (et donc de vérifier, plus tard, la performance réelle des
    croisements détectés en comparant avec les cours des jours suivants).

    Si un fichier existe déjà pour cette date (ex. relance manuelle du
    workflow le même jour), il est simplement écrasé.
    """
    os.makedirs(config.HISTORY_DIR, exist_ok=True)
    archive_path = f"{config.HISTORY_DIR}/{scan_date}.csv"
    df.to_csv(archive_path, index=False)
    return archive_path


def main():
    os.makedirs(config.DATA_DIR, exist_ok=True)

    print(f"[daily_update] Lancement du scan sur {len(config.PEA_STOCKS)} valeurs...")
    df = run_scan()

    # Fichier "courant", toujours écrasé : c'est celui que lit l'application Streamlit.
    df.to_csv(config.SCAN_RESULTS_FILE, index=False)

    # Archive datée, conservée indéfiniment : c'est la base du backtesting futur.
    if not df.empty:
        scan_date = df["date"].mode().iloc[0]  # date de session la plus fréquente du scan
    else:
        scan_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    archive_path = archive_scan(df, scan_date)

    nb_croisements = df["croisement"].notna().sum() if not df.empty else 0
    print(f"[daily_update] Scan terminé : {len(df)} valeurs traitées, "
          f"{nb_croisements} croisement(s) détecté(s).")
    print(f"[daily_update] Archive écrite : {archive_path}")

    with open(config.LAST_UPDATE_FILE, "w") as f:
        f.write(datetime.now(timezone.utc).isoformat())

    print("[daily_update] Fichiers de résultats écrits dans data/.")


if __name__ == "__main__":
    main()
