# Scanner PEA

Scanner d'actions françaises éligibles au PEA, avec mise à jour automatique
quotidienne et détection des croisements EMA9/EMA20.

## Fonctionnement

1. Chaque jour à 18h30 (heure de Paris, jours ouvrés), un **GitHub Actions**
   télécharge 2 ans de données pour toutes les actions listées dans
   `src/config.py`, calcule les indicateurs techniques et détecte les
   signaux du jour. Les résultats sont sauvegardés dans
   `data/scan_results.csv` (toujours écrasé, c'est la photo du jour) **et**
   archivés dans `data/history/AAAA-MM-JJ.csv` (jamais écrasé, un fichier
   par jour) pour permettre un futur backtesting. Le tout est commité
   automatiquement.
2. L'application **Streamlit** lit ce fichier et l'affiche sur plusieurs pages :
   - `app.py` : vue d'ensemble de toutes les actions suivies (avec score de
     tendance, RSI, croisements, cassures)
   - `pages/1_Croisements_EMA.py` : actions ayant eu un croisement EMA9/EMA20
     lors de la dernière session
   - `pages/2_RSI.py` : actions en zone de surachat (RSI > 70) ou de
     survente (RSI < 30)
   - `pages/3_Volumes.py` : actions dont le volume du jour dépasse 1,5× leur
     volume moyen (intérêt anormal du marché)
   - `pages/4_Cassures.py` : actions ayant cassé leur plus haut ou leur plus
     bas des 20 dernières séances

### Indicateurs calculés pour chaque action

- **EMA9 / EMA20 / EMA200** et détection de croisement EMA9/EMA20
- **RSI14** (indice de force relative, lissage de Wilder)
- **Volume du jour**, volume moyen sur 20 jours, et ratio jour/moyenne
- **Variation moyenne 14 jours** : amplitude haut-bas moyenne en % (volatilité récente)
- **Plus haut / plus bas 52 semaines**
- **Plus haut / plus bas 20 jours** et détection de cassure
- **Score de tendance** : compare l'ordre relatif de Prix/EMA9/EMA20/EMA200
  selon le barème suivant (les configurations non listées obtiennent un
  score neutre de 0, visible dans la colonne `configuration_tendance` du
  fichier CSV) :

  | Configuration | Score |
  |---|---|
  | Prix > EMA9 > EMA20 > EMA200 | +7 |
  | Prix > EMA20 > EMA9 > EMA200 | +4 |
  | EMA9 > Prix > EMA20 > EMA200 | +4 |
  | EMA20 > EMA9 > Prix > EMA200 | +2 |
  | EMA20 > EMA200 > Prix > EMA9 | -2 |
  | EMA200 > Prix > EMA20 > EMA9 | -4 |
  | EMA200 > EMA9 > Prix > EMA20 | -4 |
  | EMA200 > EMA20 > EMA9 > Prix | -7 |

Aucune infrastructure à gérer : tout tourne sur GitHub (calcul) et Streamlit
Community Cloud (affichage), gratuitement.

## Mise en place (100% en ligne, aucune installation locale nécessaire)

### 1. Créer le dépôt GitHub

- Va sur https://github.com/new
- Crée un nouveau dépôt (public ou privé), par exemple `pea-scanner`
- Sur la page du dépôt vide, utilise le bouton **"uploading an existing file"**
  pour glisser-déposer tous les fichiers de ce projet (en conservant
  l'arborescence des dossiers), ou utilise GitHub Desktop / l'interface web
  "Add file > Upload files".

> Astuce : GitHub permet aussi de créer les fichiers un par un directement
> dans le navigateur via "Add file > Create new file", en collant le contenu.

### 2. Vérifier les permissions du workflow

- Dans le dépôt : **Settings > Actions > General > Workflow permissions**
- Sélectionne **"Read and write permissions"**
- Sauvegarde. (Nécessaire pour que le job puisse committer `data/scan_results.csv`.)

### 3. Lancer un premier scan manuel

- Onglet **Actions** du dépôt GitHub
- Sélectionne le workflow **"Mise à jour quotidienne des données PEA"**
- Clique sur **"Run workflow"** (bouton à droite) pour générer les premières
  données sans attendre 18h30.

### 4. Déployer l'application Streamlit

- Va sur https://share.streamlit.io
- Connecte-toi avec ton compte GitHub
- Clique sur **"New app"**, sélectionne le dépôt `pea-scanner`, la branche
  `main`, et le fichier principal `app.py`
- Dans **"Advanced settings"**, vérifie que la version Python sélectionnée
  est **3.11** (ou installe le fichier `runtime.txt` fourni, qui fixe cette
  version automatiquement). Les versions très récentes de Python (3.13/3.14)
  n'ont pas toujours de wheels précompilées pour certaines dépendances
  (pandas, pillow) et forcent une compilation depuis les sources qui échoue
  sur l'environnement de build de Streamlit Cloud.
- Déploie : l'application est en ligne en quelques minutes, à une URL du type
  `https://pea-scanner-xxxx.streamlit.app`

À partir de là, l'application se met à jour automatiquement chaque jour, sans
aucune intervention manuelle.

## Étendre le projet

Le code est structuré pour évoluer facilement :

- **Ajouter des actions** : compléter la liste `PEA_STOCKS` dans `src/config.py`
- **Ajouter un indicateur** (RSI, Bollinger, MACD...) : ajouter une fonction
  dans `src/indicators.py`, l'appeler dans `src/scanner.py`
- **Ajouter une page d'analyse** : créer un nouveau fichier dans `pages/`
  (Streamlit détecte automatiquement les pages ajoutées)
- **Backtesting** : `data/history/` contient déjà un fichier par jour de scan.
  Une prochaine étape naturelle est un script `scripts/backtest.py` qui charge
  ces archives, retrouve les croisements passés, et calcule leur performance
  réelle (cours N jours après le croisement) pour valider la stratégie avant
  de s'y fier

## Structure du projet

```
pea-scanner/
├── .github/workflows/update_data.yml   # planification du scan quotidien
├── data/                                # résultats produits par le scan
├── src/
│   ├── config.py                        # liste des actions + paramètres
│   ├── data_fetcher.py                  # téléchargement yfinance (+ retry)
│   ├── indicators.py                    # calcul EMA + détection croisement
│   └── scanner.py                       # orchestration du scan
├── scripts/daily_update.py              # point d'entrée du job GitHub Actions
├── app.py                               # page d'accueil Streamlit
├── pages/1_Croisements_EMA.py           # page des croisements EMA
└── requirements.txt
```
