# User Based Recommendation

## Prérequis

### Base de données

1. Build et run le docker

    ```sh
    docker compose up --build
    ```

2. Initialiser et peupler la base de données

    Voir le [README de Track 2 BDD](../../../T2_BDD/README.md)

3. Si la BDD existait déjà avant de build le docker, ouvrez [PgAdmin](http://localhost:8081/) et exécutez le contenu de [add_vector_to_db.sql](add_vector_to_db.sql)

### Environnement python

Créez un venv et activez-le.

Linux
```sh
python3 -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell)
```sh
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Installez les dépendances.

```sh
pip install -r requirements.txt
```

## Créer les vecteurs

```sh
python scr/user_based/populate_vectors.py
```

## Recommandations

```sh
python scr/user_based/user_based.py
```

Les utilisateurs n'ont aucunes écoutes donc le résultat est vide.
