# SAE5-C-IDFou

## Track Partie 1

### Aperçu

Projet de data analyse réalisé dans le cadre de la SAÉ du 5ᵉ semestre. L'objectif est de nettoyer, fusionner et explorer différents jeux de données musicaux afin de préparer des visualisations et analyses statistiques.

### Architecture du projet

```text
.
├── cleaned_data/           # Résultats des scripts de nettoyage
├── consignes/              # Consignes officielles et dictionnaire de données
├── data/                   # Jeux de données bruts fournis
├── docs/                   # Documentation additionnelle (règles internes, notes)
├── src/                    # Scripts Python (clean, download, merge, visualisation)
└── README.md               # Vous êtes ici
```

### Préparer l'environnement

1. Installer Python 3.13 ou plus récent.
2. Créer un environnement virtuel isolé dans le dépôt :

   ```bash
   python3.13 -m venv src/.venv
   source src/.venv/bin/activate
   ```

3. Installer les dépendances :

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

### Téléchargement des données

- Scripts disponibles dans `src/download/`.
- `download_data.py` récupère l’archive Google Drive des CSV bruts.
- `download_cleaned_data.py` télécharge les versions nettoyées officielles dans `cleaned_data/`.
- `download_all.py` enchaîne les deux opérations ci-dessus.

Exemple d’utilisation (après activation de l’environnement) :

```bash
python src/download/download_all.py
```

### Jeux de données

- `data/` : dépôts CSV bruts fournis par le sujet (`echonest.csv`, `features.csv`, `genres.csv`, `raw_*`, `tracks.csv`, etc.). Ils ne doivent pas être modifiés manuellement.
- `cleaned_data/` : sorties produites par le nettoyage des donnés (`clean_*`, `merged_tracks.csv`). Chaque fichier reflète les mêmes schémas que les bruts, mais avec les lignes filtrées, les valeurs standardisées et des métadonnées de suivi.

### Nettoyage des données

#### Validation et Standardisation des données

- Point d'entrée : `src/clean/main.py`.
- Les règles de validation sont centralisées dans `src/clean/globalrules.py` (description des colonnes, types attendus, règles de standardisation).
- `src/clean/validation.py` applique ces règles et produit un rapport (`CleanReport`) affiché en console.
- `src/clean/standardisation.py` contient les transformations applicables (normalisation de texte, dates, etc.).

Exécuter l'ensemble du nettoyage :

```bash
python src/clean/main.py --data-dir data --output-dir cleaned_data --stats
```

Arguments utiles :

- `--csv FICHIER1 FICHIER2` pour cibler certains CSV.
- `--limit N` pour tester sur un sous-échantillon.
- `--stats` pour afficher le détail des règles appliquées.

#### Fusion des données sur tracks

- Point d'entrée : `src/merge/main.py`. Le script charge `clean_tracks.csv` puis fusionne séquentiellement les données de `clean_genres.csv`, `clean_raw_albums.csv`, `clean_raw_artists.csv`, `clean_features.csv`, `clean_echonest.csv` et `clean_raw_tracks.csv`.
- Les colonnes clés (`track_id`, `album_id`, `artist_id`) sont retypées en entiers nullable pour éviter les échecs de jointure, et les listes de genres sont normalisées avant l'`explode`.
- La sortie consolide les métadonnées prioritaires du jeu `clean_tracks.csv` et les complète par les attributs manquants trouvés dans les autres fichiers.
- Le fichier final est trié par `track_id` et `genre_id`, puis exporté dans `cleaned_data/merged_tracks.csv` (sauf si `--dry-run` est activé).

Exemple d'exécution :

```bash
python src/merge/main.py --data-dir cleaned_data --output cleaned_data/merged_tracks.csv
```

Le paramètre `--output` est optionnel ; sans lui, le fichier est écrit automatiquement dans le dossier passé à `--data-dir`.

### Générer les graphiques

1. Activer l'environnement virtuel :

   ```bash
   source src/.venv/bin/activate
   ```

2. Lancer l'orchestrateur :

   ```bash
   python src/graphs/run_all_graphs.py
   ```

Le script crée automatiquement un sous-répertoire par visualisation dans `outputs/<graph_name>/`.  
