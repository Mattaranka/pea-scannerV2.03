"""
Configuration centrale du scanner PEA.

Toute évolution (nouvelle action à suivre, nouveau paramètre d'indicateur)
se fait ici, sans toucher au reste du code.
"""

# --- Paramètres des indicateurs -------------------------------------------------
EMA_SHORT = 9
EMA_LONG = 20
EMA_TREND = 200  # EMA longue utilisée pour le score de tendance

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

VOLUME_AVG_PERIOD = 20      # moyenne de volume calculée sur 20 jours
VOLUME_SPIKE_RATIO = 1.5    # seuil de détection d'un volume anormal

RANGE_PERIOD = 14           # nombre de jours pour la variation moyenne (haut-bas)

HIGH_LOW_52W_WINDOW = 252   # ~52 semaines de bourse (jours ouvrés)

BREAKOUT_PERIOD = 20        # fenêtre de référence pour détecter une cassure

# Nombre de mois/années d'historique téléchargés. 2 ans sont nécessaires pour
# stabiliser l'EMA200 (qui a besoin de beaucoup de recul pour converger) et
# pour calculer un vrai plus haut/plus bas sur 52 semaines.
HISTORY_PERIOD = "2y"
HISTORY_INTERVAL = "1d"

# --- Fichiers de sortie ----------------------------------------------------------
DATA_DIR = "data"
SCAN_RESULTS_FILE = f"{DATA_DIR}/scan_results.csv"
LAST_UPDATE_FILE = f"{DATA_DIR}/last_update.txt"

# Archivage quotidien des scans (un fichier par jour), utilisé pour le
# backtesting : permet de reconstituer l'historique des croisements détectés
# et de calculer leur performance a posteriori.
HISTORY_DIR = f"{DATA_DIR}/history"

# --- Univers d'actions éligibles au PEA (CAC 40 + principales valeurs SBF120) ----
# Format : ticker Yahoo Finance (suffixe .PA pour Euronext Paris), nom, secteur.
# Cette liste est un point de départ : elle est volontairement gérée comme une
# simple structure de données pour être étendue facilement (SBF120 complet,
# CAC All-Tradable, etc.) sans modifier la logique du scanner.
PEA_STOCKS = [
    # --- CAC 40 ---
    {"ticker": "AI.PA", "nom": "Air Liquide", "secteur": "Industrie"},
    {"ticker": "AIR.PA", "nom": "Airbus", "secteur": "Aéronautique"},
    {"ticker": "ALO.PA", "nom": "Alstom", "secteur": "Industrie"},
    {"ticker": "MT.AS", "nom": "ArcelorMittal", "secteur": "Matériaux"},
    {"ticker": "CS.PA", "nom": "AXA", "secteur": "Assurance"},
    {"ticker": "BNP.PA", "nom": "BNP Paribas", "secteur": "Banque"},
    {"ticker": "EN.PA", "nom": "Bouygues", "secteur": "BTP/Télécom"},
    {"ticker": "CAP.PA", "nom": "Capgemini", "secteur": "Technologie"},
    {"ticker": "CA.PA", "nom": "Carrefour", "secteur": "Distribution"},
    {"ticker": "ACA.PA", "nom": "Crédit Agricole", "secteur": "Banque"},
    {"ticker": "BN.PA", "nom": "Danone", "secteur": "Agroalimentaire"},
    {"ticker": "DSY.PA", "nom": "Dassault Systèmes", "secteur": "Technologie"},
    {"ticker": "EDEN.PA", "nom": "Edenred", "secteur": "Services"},
    {"ticker": "ENGI.PA", "nom": "Engie", "secteur": "Énergie"},
    {"ticker": "EL.PA", "nom": "EssilorLuxottica", "secteur": "Santé/Optique"},
    {"ticker": "ERF.PA", "nom": "Eurofins Scientific", "secteur": "Santé"},
    {"ticker": "RMS.PA", "nom": "Hermès", "secteur": "Luxe"},
    {"ticker": "KER.PA", "nom": "Kering", "secteur": "Luxe"},
    {"ticker": "OR.PA", "nom": "L'Oréal", "secteur": "Cosmétiques"},
    {"ticker": "LR.PA", "nom": "Legrand", "secteur": "Industrie"},
    {"ticker": "MC.PA", "nom": "LVMH", "secteur": "Luxe"},
    {"ticker": "ML.PA", "nom": "Michelin", "secteur": "Industrie"},
    {"ticker": "ORA.PA", "nom": "Orange", "secteur": "Télécom"},
    {"ticker": "RI.PA", "nom": "Pernod Ricard", "secteur": "Boissons"},
    {"ticker": "PUB.PA", "nom": "Publicis", "secteur": "Communication"},
    {"ticker": "RNO.PA", "nom": "Renault", "secteur": "Automobile"},
    {"ticker": "SAF.PA", "nom": "Safran", "secteur": "Aéronautique"},
    {"ticker": "SGO.PA", "nom": "Saint-Gobain", "secteur": "Matériaux"},
    {"ticker": "SAN.PA", "nom": "Sanofi", "secteur": "Santé"},
    {"ticker": "SU.PA", "nom": "Schneider Electric", "secteur": "Industrie"},
    {"ticker": "GLE.PA", "nom": "Société Générale", "secteur": "Banque"},
    {"ticker": "STLAP.PA", "nom": "Stellantis", "secteur": "Automobile"},
    {"ticker": "STMPA.PA", "nom": "STMicroelectronics", "secteur": "Technologie"},
    {"ticker": "TEP.PA", "nom": "Teleperformance", "secteur": "Services"},
    {"ticker": "HO.PA", "nom": "Thales", "secteur": "Défense"},
    {"ticker": "TTE.PA", "nom": "TotalEnergies", "secteur": "Énergie"},
    {"ticker": "URW.PA", "nom": "Unibail-Rodamco-Westfield", "secteur": "Immobilier"},
    {"ticker": "VIE.PA", "nom": "Veolia", "secteur": "Environnement"},
    {"ticker": "DG.PA", "nom": "Vinci", "secteur": "BTP"},
    {"ticker": "VIV.PA", "nom": "Vivendi", "secteur": "Médias"},
    # --- Autres valeurs SBF120 / mid-caps courantes ---
    {"ticker": "ATO.PA", "nom": "Atos", "secteur": "Technologie"},
    {"ticker": "SOI.PA", "nom": "Soitec", "secteur": "Semi-conducteurs"},
    {"ticker": "NANO.PA", "nom": "Nanobiotix", "secteur": "Biotech"},
    {"ticker": "ADOC.PA", "nom": "Adocia", "secteur": "Biotech"},
    {"ticker": "BVI.PA", "nom": "Bureau Veritas", "secteur": "Services"},
    {"ticker": "CO.PA", "nom": "Casino Guichard", "secteur": "Distribution"},
    {"ticker": "COFA.PA", "nom": "Coface", "secteur": "Assurance"},
    {"ticker": "GET.PA", "nom": "Getlink", "secteur": "Transport"},
    {"ticker": "ICAD.PA", "nom": "Icade", "secteur": "Immobilier"},
    {"ticker": "IPN.PA", "nom": "Ipsen", "secteur": "Santé"},
    {"ticker": "IPS.PA", "nom": "Ipsos", "secteur": "Services"},
    {"ticker": "IPH.PA", "nom": "InnatePharma", "secteur": "Biotech"},
    {"ticker": "JCQ.PA", "nom": "Jacquet Metal Service", "secteur": "Industrie"},
    {"ticker": "MERY.PA", "nom": "Mercialys", "secteur": "Immobilier"},
    {"ticker": "NEX.PA", "nom": "Nexans", "secteur": "Industrie"},
    {"ticker": "RUI.PA", "nom": "Rubis", "secteur": "Énergie"},
    {"ticker": "SESL.PA", "nom": "SES-imagotag", "secteur": "Technologie"},
    {"ticker": "SW.PA", "nom": "Sodexo", "secteur": "Services"},
    {"ticker": "SPIE.PA", "nom": "Spie", "secteur": "Services"},
    {"ticker": "SK.PA", "nom": "SEB", "secteur": "Biens de consommation"},
    {"ticker": "TFI.PA", "nom": "TF1", "secteur": "Médias"},
    {"ticker": "TKO.PA", "nom": "Tikehau Capital", "secteur": "Finance"},
    {"ticker": "VLA.PA", "nom": "Valneva", "secteur": "Biotech"},
    {"ticker": "VK.PA", "nom": "Vallourec", "secteur": "Industrie"},
    {"ticker": "VRLA.PA", "nom": "Verallia", "secteur": "Industrie"},
    {"ticker": "WLN.PA", "nom": "Worldline", "secteur": "Technologie"},
    {"ticker": "XFAB.PA", "nom": "X-FAB", "secteur": "Semi-conducteurs"},
]
