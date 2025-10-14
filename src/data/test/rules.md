# Validation et standardisation

## Règles de standardisation (`standardisation.py`)

Les règles de standardisation préparent les valeurs pour respecter un format commun avant validation.

### Type

- toInt: convertir en integer (ex: “42” → 42).
- toFloat: convertir en float (ex: “3.14” → 3.14).
- toDouble: convertir en double (ex: “3.14” → 3.14).
- toString: convertir en string (ex: 42 → “42”).
- toBoolean: convertir en boolean (ex: “true” → True, “false” → False).
- toArray: convertir les structures de type liste (ex: "1,2,3" ou "[1, 2, 3]" ou "['1', '2', '3']") en list JSON.
- parseDate: convertir “2008/11/26” ou “26-11-2008” en format ISO YYYY-MM-DD. 


### Qualité

- toLowerCase: uniformiser les chaînes (“Hip-Hop” → “hip-hop”). 
- toUpperCase: uniformiser les chaînes (“us” → “US”). 
- trimSpaces: supprimer les espaces en début et fin de chaîne (“ Rock ” → “Rock”). 
- normalizeDuration: convertir “3:45” ou “00:03:45” en secondes.
- extractGenreIds: convertit une colonne contenant des dictionnaires ou chaînes en liste d'identifiants numériques.
- normalizeTags: uniformise une colonne de tags en liste de chaînes nettoyées.

## Règles de validation (`validation.py`)

Les règles de validation décrivent les contraintes appliquées après standardisation éventuelle.

### Type

- int: la valeur doit être un integer (conversion automatique depuis string/float).
- float: la valeur doit être un float.
- double: la valeur doit être un double.
- string: la valeur doit être un String.
- date: la valeur doit être un Date au format AAAA-MM-DD.
- boolean: la valeur doit être un boolean.
- array: combiner avec un autre type pour préciser le type du contenu de l'array.

### Qualité

- notNull: La valeur ne peut pas être NULL
- notNegative: La valeur doit ne peut être < 0
- positiveNumber: La valeur doit être strictement > 0
- unique: La valeur ne doit pas être dupliquée dans la colonne
- isLowerCase: La valeur doit être un string et en lower case
- isUpperCase: La valeur doit être en uppercase
- beforeNow: La valeur doit être une date inférieure à now
- afterNow: La valeur doit être une date supérieur à now

## Application des règles

### raw_tracks.csv

```json
 "raw_tracks.csv": {
        "header_rows": [0],
        "skip_rows": [],
        "rename_columns": {},
        "standardisation_rules": {
            "track_id": ["toInt"],
            "album_id": ["toInt"],
            "artist_id": ["toInt"],
            "track_number": ["toInt"],
            "track_disc_number": ["toInt"],
            "track_favorites": ["toInt"],
            "track_listens": ["toInt"],
            "track_interest": ["toDouble"],
            "track_comments": ["toInt"],
            "track_title": ["trimSpaces", "toString"],
            "track_duration": ["normalizeDuration", "toInt"],
            "track_bit_rate": ["toInt"],
            "track_genres": ["extractGenreIds", "toArray"],
            "tags": ["normalizeTags", "toArray"],
            "track_composer": ["trimSpaces", "toString"],
            "track_lyricist": ["trimSpaces", "toString"],
            "track_publisher": ["trimSpaces", "toString"],
            "track_explicit": ["toBoolean"],
            "track_instrumental": ["toBoolean"],
            "track_date_created": ["parseDate"],
            "album_title": ["trimSpaces", "toString"],
            "artist_name": ["trimSpaces", "toString"]
        },
        "validation_rules": {
            "track_id": ["notNull", "unique", "notNegative", "int"],
            "album_id": ["notNull", "notNegative", "int"],
            "artist_id": ["notNull", "notNegative", "int"],
            "track_number": ["notNegative", "int"],
            "track_disc_number": ["notNegative", "int"],
            "track_favorites": ["notNull", "notNegative", "int"],
            "track_listens": ["notNull", "notNegative", "int"],
            "track_interest": ["notNull", "notNegative", "double"],
            "track_comments": ["notNull", "notNegative", "int"],
            "track_title": ["notNull", "string"],
            "track_duration": ["notNull", "notNegative", "int"],
            "track_bit_rate": ["notNegative", "int"],
            "track_genres": ["string"],
            "tags": ["string"],
            "track_composer": ["string"],
            "track_lyricist": ["string"],
            "track_publisher": ["string"],
            "track_explicit": ["boolean"],
            "track_instrumental": ["boolean"],
            "track_date_created": ["notNull", "beforeNow", "date"],
            "album_title": ["string"],
            "artist_name": ["string"],
        },
    },
```

### tracks.csv

```json
    "tracks.csv": {
        "header_rows": [0, 1],
        "skip_rows": [0],
        "rename_columns": {
            "level_0_level_1": "track_id"
        },
        "standardisation_rules": {
            "track_id": ["toInt"],
            "album_id": ["toInt"],
            "artist_id": ["toInt"],
            "track_title": ["trimSpaces", "toString"],
            "track_duration": ["normalizeDuration", "toInt"],
            "track_genre_top": ["trimSpaces", "toString"],
            "track_genres": ["extractGenreIds", "toArray"],
            "track_tags": ["normalizeTags", "toArray"],
            "track_listens": ["toInt"],
            "track_favorites": ["toInt"],
            "track_interest": ["toFloat"],
            "track_comments": ["toInt"],
            "track_date_created": ["parseDate"],
            "track_composer": ["trimSpaces", "toString"],
            "track_lyricist": ["trimSpaces", "toString"],
            "track_publisher": ["trimSpaces", "toString"]
        },
        "validation_rules": {
            "track_id": ["notNull", "unique", "notNegative", "int"],
            "track_title": ["notNull", "string"],
            "track_duration": ["notNull", "notNegative", "int"],
            "track_genre_top": ["string"],
            "track_genres": ["string", "array"],
            "track_tags": ["string", "array"],
            "track_listens": ["notNull", "notNegative", "int"],
            "track_favorites": ["notNull", "notNegative", "int"],
            "track_interest": ["notNull", "notNegative", "float"],
            "track_comments": ["notNull", "notNegative", "int"],
            "track_date_created": ["notNull", "beforeNow", "date"],
            "track_composer": ["string"],
            "track_lyricist": ["string"],
            "track_publisher": ["string"],
            "album_id": ["notNull", "notNegative", "int"],
            "artist_id": ["notNull", "notNegative", "int"]
        }
    }
```

### raw_albums.csv

```json
    "raw_albums.csv": {
        "header_rows": [0],
        "skip_rows": [],
        "rename_columns": {},
        "standardisation_rules": {
            "album_id": ["toInt"],
            "album_title": ["trimSpaces", "toString"],
            "album_type": ["trimSpaces", "toString"],
            "album_tracks": ["toInt"],
            "album_date_released": ["parseDate"],
            "album_listens": ["toInt"],
            "album_favorites": ["toInt"],
            "album_comments": ["toInt"],
            "album_producer": ["trimSpaces", "toString"],
            "tags": ["normalizeTags", "toArray"]
        },
        "validation_rules": {
            "album_id": ["notNull", "unique", "int", "notNegative"],
            "album_title": ["notNull", "string"],
            "album_type": ["notNull", "string"],
            "album_tracks": ["notNull", "int", "positiveNumber"],
            "album_date_released": ["date", "beforeNow"],
            "album_listens": ["notNull", "int", "notNegative"],
            "album_favorites": ["notNull", "int", "notNegative"],
            "album_comments": ["notNull", "int", "notNegative"],
            "album_producer": ["string"],
            "tags": ["array", "string"]
        }
    }
```


### features.csv

```json
    "features.csv": {
        "header_rows": [0, 1],
        "skip_rows": [0, 1],
        "rename_columns": {
            "feature_statistics": "track_id"
        },
        "standardisation_rules": {
            "track_id": ["toInt"],
            "__all__": ["toFloat"]
        },
        "validation_rules": {
            "track_id": ["notNull", "int"],
            "__all__": ["notNull", "float"]
        }
    }
```
> Note: la clé spéciale `"__all__"` applique les règles à chaque colonne qui n'a pas de configuration dédiée.
