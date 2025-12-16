# Neural Network for Track Listens – Plan

## 1) Quick database reconnaissance (done)
- Base table `track` → 102 141 lignes, cible `track_listens` (aucun `NULL`, 1 valeur à 0), autres champs exploitables : `track_duration`, `track_number`, `track_disc_number`, `track_favorites`, `track_interest`, `track_comments`, `track_date_created` (pas de champs explicite/instrumental renseignés : 100 % `NULL`).
- `audio_feature` → 102 141 lignes, 8 descripteurs audio (acousticness, danceability, energy, instrumentalness, liveness, speechiness, tempo, valence) complet pour chaque piste.
- `temporal_feature` → 102 141 lignes, 519 descripteurs temporels (mfcc, chroma, spectral…, métriques stats), aucun `NULL` apparent. **Décision : on ne les utilisera pas pour limiter la largeur des features.**
- Métadonnées associées : `album` (19 844 albums, dates manquantes sur ~5 k), relations `track_genre` (100 407 pistes avec ≥1 genre, 163 genres), `track_tag` (22 678 pistes avec tags), `track_artist_main` (1 artiste principal par piste), `rank_track` (au moins une entrée par piste, rank récent à sélectionner), `playlist_track` (interactions utilisateur potentielles mais non essentielles).

## 2) Feature scope (V1 validé)
- **Seule table utilisée** : `track`.
- Colonnes retenues : `track_duration`, `track_number`, `track_disc_number`, `track_favorites`, `track_interest`, `track_comments`, `track_date_created` (convertie en année/âge), cible `track_listens`.
- **Exclus** : audio_feature, temporal_feature, genres/tags, ranks, album, artistes, explicit/instrumental, playlist.

## 3) Données → pipeline
- Ajouter un loader dédié (`db.py` / `data_loader.py`) pointant sur `sae5db` via `.env`.
- Requêtes SQL :
  - Uniquement la table `track` avec les colonnes listées plus haut.
- Export en DataFrame unique, indexé par `track_id`.

## 4) Préprocessing
- Nettoyage : coercition numérique, remplissage médian pour rares `NULL`, dates → années/âges, normalisation standard (z-score).
- Cible : `log1p(track_listens)` pour réduire la forte asymétrie (min 0, médiane 753, p90 4 818, max 543 252).
- Pas d’encodage catégoriel en V1 (aucune feature catégorielle retenue).

## 5) Dataset & split
- Séparer en 80 % train / 20 % test avec `train_test_split(random_state=42, shuffle=True)`.
- Torch `TensorDataset` + `DataLoader` (batch configurable, shuffle sur train).

## 6) Modèle
- Réseau dense (MLP) : entrée normalisée, 2–3 couches cachées (ReLU), dropout, éventuellement batchnorm.
- Loss : MSE sur `log1p` (ou MAE en métrique secondaire).
- Optimizer : Adam (LR configurable) + scheduler optionnel.
- Early-stopping / meilleur modèle sauvegardé sur validation (prendre 10–15 % du train ou k-fold simple).

## 7) Entraînement & suivi
- Script `train.py` : charge données, split 80/20, boucle d’entraînement (zero_grad/backward/step), logs pertes train/val par époque, sauvegarde `model.pt` + métadonnées (normalisation, classes genres, hyperparams).
- Mesures rapportées : RMSE/MAE sur jeu test (en échelle listens via expm1 pour lisibilité).
- Config JSON pour hyperparams par défaut (epochs, batch_size, lr, hidden_dims, dropout, top_k_genres, pca flag, etc.).

## 8) Inférence
- Script `infer.py` : charge artefacts, applique même préprocess à un `track_id` existant (ou dataset fourni) en récupérant les features DB, renvoie prédiction listens (désexp via `expm1`).
- Vérif cohérence des champs requis (durée, genres, audio) et valeurs manquantes.

## 9) Organisation des fichiers (à créer sous `neural_network_listens/`)
- `config.py` / `config.json` : lecture des hyperparams (top_k non utilisé en V1 mais conservé pour évolutions).
- `db.py` : connexion PG (reuse de `.env` racine).
- `data_loader.py` : requête unique table `track`.
- `preprocessing.py` : nettoyage, normalisation, split.
- `model.py` : définition du MLP.
- `train.py` : pipeline complet + sauvegarde.
- `test.py` : évalue sur le split test (20 %) avec les artefacts entraînés.
- `infer.py` : chargement modèle et prédiction pour un track existant (via `track_id`) en récupérant les features en base.
- `artifacts/` : sortie modèle & résumé.

## 10) Validation & next steps
- Tests rapides : sur un sous-échantillon pour valider pipeline, puis run complet.
- Ajustements envisagés : tuning hyperparams, ajout éventuel de PCA si on réintroduit des features nombreuses, essais sur cible brute vs log.

## Questions ouvertes
- Aucune pour V1 : specs figées sur la table `track` seule.
