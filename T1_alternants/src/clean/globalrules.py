from __future__ import annotations
from typing import TypedDict, Literal, NotRequired
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

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
        "rename_columns": {},
        "standardisation_rules": {
            "Horodateur": ["parseDate"],
            "Pour être sûr ": ["trimEmoji", "trimSpaces", "toString"],
            "Écoutez-vous de la musique ? ": ["trimEmoji", "trimSpaces", "toBoolean"],
            "🗓️🎵 À quelle fréquence écoutez-vous de la musique ?": ["trimEmoji", "trimSpaces", "toString"],
            "🏘️🎵 Dans quel(s) contexte(s) écoutez-vous vos musiques ?": ["trimEmoji", "trimSpaces", "toString", "toArray"],
            "🌞🎵 À quel moment de la journée écoutez-vous le plus de la musique ? ": ["trimEmoji", "trimSpaces", "toString"],
            "❓🎵 Comment écoutez-vous vos musiques ?": ["trimEmoji", "trimSpaces", "toString", "toArray"],
            "📱🎵 Quelle(s) plateforme(s) de streaming utilisez-vous ?": ["trimEmoji", "trimSpaces", "toString", "toArray"],
            "🧐🎵 Vos musiques servent à :": ["trimEmoji", "trimSpaces", "toString", "toArray"],
            "🔡🎵 Quels sont vos genres de musique préférés": ["trimEmoji", "trimSpaces", "toString", "toArray"],
            "⏰🎵 Quelle est la durée moyenne des musiques que vous écoutez ?": ["trimEmoji", "trimSpaces", "toString"],
            "🎧🎵 Écoutez-vous plutôt des morceaux ": ["trimEmoji", "trimSpaces", "toString"],
            "🚲🎵 Quel est le tempo des musiques que vous écoutez ?": ["trimEmoji", "trimSpaces", "toString"],
            "👂🎵 Les musiques que vous écoutez sont plutôt": ["trimEmoji", "trimSpaces", "toString"],
            "🔴🎵 Écoutez-vous des musiques interprétées en live ? (concert par exemple)": ["trimEmoji", "trimSpaces", "toString"],
            "🔊🎵 La qualité de l'audio est importante pour moi": ["trimEmoji", "trimSpaces", "toString"],
            "💪🎵 A quel point êtes vous prêt(e) à découvrir de nouveaux genres ou artistes ?": ["trimEmoji", "trimSpaces", "toString"],
            "📊 Quelle est votre tranche d'âge ?": ["trimEmoji", "trimSpaces", "toString"],
            "👤 Quel est votre genre ?": ["trimEmoji", "trimSpaces", "toString"],
            "👔 Dans quel domaine travaillez-vous ?": ["trimEmoji", "trimSpaces", "toString"]
        },
        "validation_rules": {
            "Horodateur": ["notNull", "beforeNow", "date"],
            "Pour être sûr ": ["notNull", "string"],
            "Écoutez-vous de la musique ? ": ["notNull", "boolean"],
            "🗓️🎵 À quelle fréquence écoutez-vous de la musique ?": ["notNull", "string"],
            "🏘️🎵 Dans quel(s) contexte(s) écoutez-vous vos musiques ?": ["notNull", "string"],
            "🌞🎵 À quel moment de la journée écoutez-vous le plus de la musique ? ": ["notNull", "string"],
            "❓🎵 Comment écoutez-vous vos musiques ?": ["notNull", "string"],
            "📱🎵 Quelle(s) plateforme(s) de streaming utilisez-vous ?": ["notNull", "string"],
            "🧐🎵 Vos musiques servent à :": ["notNull", "string"],
            "🔡🎵 Quels sont vos genres de musique préférés": ["notNull", "string"],
            "⏰🎵 Quelle est la durée moyenne des musiques que vous écoutez ?": ["notNull", "string"],
            "🎧🎵 Écoutez-vous plutôt des morceaux ": ["notNull", "string"],
            "🚲🎵 Quel est le tempo des musiques que vous écoutez ?": ["notNull", "string"],
            "👂🎵 Les musiques que vous écoutez sont plutôt": ["notNull", "string"],
            "🔴🎵 Écoutez-vous des musiques interprétées en live ? (concert par exemple)": ["notNull", "string"],
            "🔊🎵 La qualité de l'audio est importante pour moi": ["notNull", "string"],
            "💪🎵 A quel point êtes vous prêt(e) à découvrir de nouveaux genres ou artistes ?": ["notNull", "string"],
            "📊 Quelle est votre tranche d'âge ?": ["notNull", "string"],
            "👤 Quel est votre genre ?": ["notNull", "string"],
            "👔 Dans quel domaine travaillez-vous ?": ["notNull", "string"]
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
