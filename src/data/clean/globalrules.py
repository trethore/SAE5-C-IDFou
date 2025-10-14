from __future__ import annotations
from typing import TypedDict, Literal, NotRequired
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DEFAULT_DATA_DIR = PROJECT_ROOT / "data"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "out"

type validation_rule_name = Literal[
    "notNull",
    "notNegative",
    "toLowerCase",
    "toUpperCase",
    "beforeNow",
    "afterNow",
    "int",
    "string",
    "float",
    "double",
    "boolean",
    "array",
    "date",
]

type standardisation_rule_name = Literal[
    "toLowerCase",
    "toUpperCase",
    "trimSpaces",
    "parseDate",
    "normalizeDuration",
    "extractGenreIds",
    "normalizeTags",
    "normalizeBoolean",
    "toArray",
    "toInt",
    "toFloat",
    "toDouble",
    "toString",
    "toBoolean",
]

class CsvConfig(TypedDict):
    header_rows: list[int]
    skip_rows: list[int]
    rename_columns: dict[str, str]
    validation_rules: dict[str, list[validation_rule_name]]
    standardisation_rules: NotRequired[dict[str, list[standardisation_rule_name]]]

type RulesByCsv = dict[str, CsvConfig]


RULES_BY_CSV: RulesByCsv = {
    "tracks.csv": {
        "header_rows": [0, 1],
        "skip_rows": [0],
        "rename_columns": {
            "level_0_level_1": "track_id",
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
            "track_publisher": ["trimSpaces", "toString"],
        },
        "validation_rules": {
            "track_id": ["notNull", "notNegative", "int"],
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
            "artist_id": ["notNull", "notNegative", "int"],
        },
    },
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
            "artist_name": ["trimSpaces", "toString"],
        },
        "validation_rules": {
            "track_id": ["notNull", "notNegative", "int"],
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
}


def get_rules() -> RulesByCsv:
    return RULES_BY_CSV


def get_rule_for(csv_name: str) -> CsvConfig | None:
    return RULES_BY_CSV.get(csv_name)


__all__ = [
    "DEFAULT_DATA_DIR",
    "DEFAULT_OUTPUT_DIR",
    "RULES_BY_CSV",
    "get_rules",
    "get_rule_for",
]
