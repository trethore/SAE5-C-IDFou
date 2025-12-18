# Item-based Recommender (v2) — usage rapide

Ce README donne les commandes à exécuter **depuis ce dossier** (`T3_Recommandation/src/item_based_audio`).

## Pré-requis
- Docker (pour la base PostgreSQL) et les services du dépôt démarrés. Si besoin, démarre la DB depuis n'importe quel dossier avec :

```bash
# depuis la racine du dépôt
docker compose up sae5db
```

- Un environnement Python avec les dépendances :

```bash
# crée un virtualenv local dans ce dossier
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install numpy pandas scikit-learn scipy psycopg2-binary
```


## Commandes (en partant de ce dossier)

```bash
export $(grep -v '^#' .env | xargs)
```

- Lancer la recommandation **MK2 (audio-weight + bruit aléatoire)** :
```bash
# exemple : audio 75% et un petit bruit (reproductible avec --random-seed)
PYTHONPATH="T3_Recommandation/src" .venv/bin/python -m item_based_audio.cli --track-id 0eef0068-99b1-45a1-92f1-57c277bb9501 --n 10 --audio-weight 0.75 --random-noise 0.01 --random-seed 1
```

- Sauvegarder la sortie dans un fichier :
```bash
PYTHONPATH=".." .venv/bin/python -m item_based_audio.cli --track-id <TRACK_ID> --n 20 > recommandations.txt
```

## Notes pratiques
- Si `--random-noise > 0` et que **`--random-seed` est donné**, les résultats sont reproductibles. Sans seed, l'ordre peut varier.
- Si la connexion DB échoue, le loader tente de replier sur `data/clean_tracks.csv` (si présent).

## Requêtes utiles (depuis ce dossier)
- Obtenir le titre d'une piste (sans quitter ce dossier) :
```bash
docker compose -f ../../../docker-compose.yml exec -T sae5db psql -U idfou -d sae5idfou -t -c "SELECT track_title FROM track WHERE track_id = '<TRACK_ID>' LIMIT 1;"
```

- Lister les audio_features non vides (exemple limité à 100 lignes) :
```bash
docker compose -f ../../../docker-compose.yml exec -T sae5db psql -U idfou -d sae5idfou -c "SELECT * FROM audio_feature WHERE acousticness IS NOT NULL LIMIT 100;"
```




