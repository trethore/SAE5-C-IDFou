# Validation et standardisation

## Règles de standardisation (`standardisation.py`)

Les règles de standardisation préparent les valeurs pour respecter un format commun avant validation.

- toLowerCase: uniformiser les chaînes (“Hip-Hop” → “hip-hop”). 
- toUpperCase: uniformiser les chaînes (“us” → “US”). 
- trimSpaces: supprimer les espaces en début et fin de chaîne (“ Rock ” → “Rock”). 
- parseDate: convertir “2008/11/26” ou “26-11-2008” en format ISO YYYY-MM-DD. 
- normalizeDuration: convertir “3:45” ou “00:03:45” en secondes.
- toArray: convertir une chaîne séparée par des virgules en liste (ex: "rock, pop" → ["rock", "pop"]), convertir tout et n’importe quoi en list[T] homogène, (ex: [1,2,3] ou "['1','2','3']" ou ['1','2','3']).
- extract_genre_ids: convertit une colonne contenant des dictionnaires ou chaînes en liste d'identifiants numériques.
- normalize_tags: uniformise une colonne de tags en liste de chaînes nettoyées.

## Règles de validation (`validation.py`)

Les règles de validation décrivent les contraintes appliquées après standardisation éventuelle.

### Type

- int: la valeur doit être un integer (conversion automatique depuis string/float).
- float: la valeur doit être un float.
- string: la valeur doit être un String.
- date: la valeur doit être un Date au format AAAA-MM-DD.
- boolean: la valeur doit être un boolean.
- array: combiner avec un autre type pour préciser le type du contenu de l'array.

### Qualité

- notNull: La valeur ne peut pas être NULL
- notNegative: La valeur doit ne peut être < 0
- isLowerCase: La valeur doit être un string et en lower case
- isUpperCase: La valeur doit être en uppercase
- beforeNow: La valeur doit être une date inférieure à now
- afterNow: La valeur doit être une date supérieur à now

## Application des règles

Tracks:

"track_id": notNull, notNegative, int
"track_title": notNull, string
"track_duration": notNull, notNegative, float
"track_genre_top": string
"track_genres": array
"track_tags": string, array
"track_listens": notNull, notNegative, int
"track_favorites": notNull, notNegative, int
"track_interest": notNull, notNegative, float
"track_comments": notNull, notNegative, int
"track_date_created": notNull, beforeNow, date
"track_date_recorded": notNull, date
"track_composer": string
"track_lyricist": string
"track_publisher": string
"album_id": notNull, notNegative, int
"artist_id": notNull, notNegative, int

Raw_Tracks:

"track_id": notNull, notNegative, int
"album_id": notNull, notNegative, int
"artist_id": notNull, notNegative, int
"track_number": notNegative, int
"track_disc_number": notNegative, int
"track_favorites": notNull, notNegative, int
"track_listens": notNull, notNegative, int
"track_interest": notNull, notNegative, float
"track_comments": notNull, notNegative, int
"track_title": notNull, string
"track_duration": notNull, timecode
"track_bit_rate": notNegative, int
"track_genres": array
"tags": array
"track_composer": string
"track_lyricist": string
"track_publisher": string
"track_explicit": boolean
"track_instrumental": boolean
"track_language_code": string, toUpperCase
"track_date_created": notNull, beforeNow, date
"track_date_recorded": notNull, date
"album_title": string
"artist_name": string
