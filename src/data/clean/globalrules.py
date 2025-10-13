from __future__ import annotations
from typing import TypedDict, Literal
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DEFAULT_DATA_DIR = PROJECT_ROOT / "data"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "out"

type rule_name = Literal[
    "notNull",
    "notNegative",
    "int",
    "string",
    "float",
    "array",
    "beforeNow",
    "date",
]


class CsvConfig(TypedDict):
    header_rows: list[int]
    skip_rows: list[int]
    rename_columns: dict[str, str]
    column_rules: dict[str, list[rule_name]]

type RulesByCsv = dict[str, CsvConfig]


RULES_BY_CSV: RulesByCsv = {
    "tracks.csv": {
        "header_rows": [0, 1],
        "skip_rows": [0],
        "rename_columns": {
            "level_0_level_1": "track_id",
        },
        "column_rules": {
            "track_id": ["notNull", "notNegative", "int"],
            "track_title": ["notNull", "string"],
            "track_duration": ["notNull", "notNegative", "float"],
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

