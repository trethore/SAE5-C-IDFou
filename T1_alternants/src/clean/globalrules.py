from __future__ import annotations
from typing import TypedDict, Literal, NotRequired
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DEFAULT_GRAPHS_FOLDER = PROJECT_ROOT / "T1_alternants" / "src" / "graphs"
DEFAULT_CONVERTION_RULES = PROJECT_ROOT / "T1_alternants" / "src" / "clean"
DEFAULT_DATA_DIR = PROJECT_ROOT / "data"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "out"

type validation_rule_name = Literal[
    "notNull",
    "notNegative",
    "positiveNumber",
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
    "unique",
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
    "trimEmoji",
    "convertToQuantitative"
]

class CsvConfig(TypedDict):
    header_rows: list[int]
    skip_rows: list[int]
    rename_columns: dict[str, str]
    validation_rules: dict[str, list[validation_rule_name]]
    standardisation_rules: NotRequired[dict[str, list[standardisation_rule_name]]]

type RulesByCsv = dict[str, CsvConfig]


RULES_BY_CSV: RulesByCsv = {
    "answers.csv": {
        "header_rows": [0],
        "skip_rows": [],
        "rename_columns": {
            "Horodateur": "created_at",
            "Pour être sûr ": "has_consented",
            "Écoutez-vous de la musique ? ": "is_listening",
            "🗓️🎵 À quelle fréquence écoutez-vous de la musique ?": "frequency",
            "🏘️🎵 Dans quel(s) contexte(s) écoutez-vous vos musiques ?": "context",
            "🌞🎵 À quel moment de la journée écoutez-vous le plus de la musique ? ": "when",
            "❓🎵 Comment écoutez-vous vos musiques ?": "how",
            "📱🎵 Quelle(s) plateforme(s) de streaming utilisez-vous ?": "platform",
            "🧐🎵 Vos musiques servent à :": "utility",
            "🔡🎵 Quels sont vos genres de musique préférés": "music_genre",
            "⏰🎵 Quelle est la durée moyenne des musiques que vous écoutez ?": "duration",
            "🎧🎵 Écoutez-vous plutôt des morceaux ": "energy",
            "🚲🎵 Quel est le tempo des musiques que vous écoutez ?": "tempo",
            "👂🎵 Les musiques que vous écoutez sont plutôt": "feeling",
            "🔴🎵 Écoutez-vous des musiques interprétées en live ? (concert par exemple)": "is_live",
            "🔊🎵 La qualité de l'audio est importante pour moi": "quality",
            "💪🎵 A quel point êtes vous prêt(e) à découvrir de nouveaux genres ou artistes ?": "curiosity",
            "📊 Quelle est votre tranche d'âge ?": "age_range",
            "👤 Quel est votre genre ?": "gender",
            "👔 Dans quel domaine travaillez-vous ?": "position"
        },
        "standardisation_rules": {
            "created_at": ["parseDate"],
            "has_consented": ["trimEmoji", "trimSpaces", "toString"],
            "is_listening": ["trimEmoji", "trimSpaces", "toBoolean"],
            "frequency": ["trimEmoji", "trimSpaces", "toString"],
            "context": ["trimEmoji", "trimSpaces", "toString", "toArray"],
            "when": ["trimEmoji", "trimSpaces", "convertToQuantitative"],
            "how": ["trimEmoji", "trimSpaces", "toString", "toArray"],
            "platform": ["trimEmoji", "trimSpaces", "toString", "toArray"],
            "utility": ["trimEmoji", "trimSpaces", "toString", "toArray"],
            "music_genre": ["trimEmoji", "trimSpaces", "toString", "toArray"],
            "duration": ["trimEmoji", "trimSpaces", "convertToQuantitative"],
            "energy": ["trimEmoji", "trimSpaces", "toString"],
            "tempo": ["trimEmoji", "trimSpaces", "convertToQuantitative"],
            "feeling": ["trimEmoji", "trimSpaces", "toString"],
            "is_live": ["trimEmoji", "trimSpaces", "toString"],
            "quality": ["trimEmoji", "trimSpaces", "convertToQuantitative"],
            "curiosity": ["trimEmoji", "trimSpaces", "convertToQuantitative"],
            "age_range": ["trimEmoji", "trimSpaces", "toString"],
            "gender": ["trimEmoji", "trimSpaces", "toString"],
            "position": ["trimEmoji", "trimSpaces", "toString"]
        },
        "validation_rules": {
            "created_at": ["notNull", "beforeNow", "date"],
            "has_consented": ["notNull", "string"],
            "is_listening": ["notNull", "boolean"],
            "frequency": ["notNull", "string"],
            "context": ["notNull", "string"],
            "when": ["notNull", "float", "positiveNumber"],
            "how": ["notNull", "string"],
            "platform": ["notNull", "string"],
            "utility": ["notNull", "string"],
            "music_genre": ["notNull", "string"],
            "duration": ["notNull", "float", "positiveNumber"],
            "energy": ["notNull", "string"],
            "tempo": ["notNull", "float", "positiveNumber"],
            "feeling": ["notNull", "string"],
            "is_live": ["notNull", "string"],
            "quality": ["notNull", "float", "positiveNumber"],
            "curiosity": ["notNull", "float", "positiveNumber"],
            "age_range": ["notNull", "string"],
            "gender": ["notNull", "string"],
            "position": ["notNull", "string"]
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
