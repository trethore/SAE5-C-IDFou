from __future__ import annotations

import ast
from typing import Any, Callable

import pandas as pd

StandardisationFn = Callable[[Any], Any]


def _is_nan(value: Any) -> bool:
    return pd.isna(value)


def _safe_literal_eval(raw: str) -> Any:
    try:
        return ast.literal_eval(raw)
    except (ValueError, SyntaxError):
        return None


def _coerce_sequence(raw: Any) -> list[Any] | None:
    if isinstance(raw, list):
        return raw
    if isinstance(raw, tuple):
        return list(raw)
    if not isinstance(raw, str):
        return None

    text = raw.strip()
    if not text:
        return []

    parsed = _safe_literal_eval(text)
    if parsed is None:
        normalized = (
            text.replace("null", "None")
            .replace("true", "True")
            .replace("false", "False")
        )
        parsed = _safe_literal_eval(normalized)

    if isinstance(parsed, list):
        return parsed
    if isinstance(parsed, tuple):
        return list(parsed)

    return None


def extract_genre_ids(value: Any) -> Any:
    if _is_nan(value):
        return value

    sequence = _coerce_sequence(value)
    if sequence is None:
        return []

    genre_ids: list[int] = []
    for item in sequence:
        candidate = None
        if isinstance(item, dict):
            candidate = item.get("genre_id")
        elif isinstance(item, (str, int)):
            candidate = item

        if candidate is None:
            continue

        try:
            genre_ids.append(int(candidate))
        except (TypeError, ValueError):
            continue

    return genre_ids


def normalize_tags(value: Any) -> Any:
    if _is_nan(value):
        return value

    sequence = _coerce_sequence(value)
    if sequence is None:
        return []

    cleaned: list[str] = []
    for item in sequence:
        if isinstance(item, (str, int, float)):
            text = str(item).strip()
            if text:
                cleaned.append(text)
        elif isinstance(item, dict):
            # use common keys if present
            text = item.get("name") or item.get("tag") or item.get("value")
            if isinstance(text, str):
                text = text.strip()
                if text:
                    cleaned.append(text)
    return cleaned


def _apply_string_transform(value: Any, transform: Callable[[str], str]) -> Any:
    if _is_nan(value):
        return value

    if isinstance(value, str):
        return transform(value)

    if isinstance(value, (list, tuple)):
        transformed: list[Any] = []
        for item in value:
            if isinstance(item, str):
                transformed.append(transform(item))
            else:
                transformed.append(item)
        return transformed

    return value


def to_lower_case(value: Any) -> Any:
    return _apply_string_transform(value, lambda text: text.lower())


def to_upper_case(value: Any) -> Any:
    return _apply_string_transform(value, lambda text: text.upper())


def trim_spaces(value: Any) -> Any:
    return _apply_string_transform(value, lambda text: text.strip())


def parse_date(value: Any) -> Any:
    if _is_nan(value):
        return value

    if isinstance(value, str):
        candidate = value.strip()
        if not candidate:
            return value
    else:
        candidate = value

    timestamp = pd.to_datetime(candidate, errors="coerce")
    if pd.isna(timestamp):
        return value
    return timestamp.strftime("%Y-%m-%d")


def normalize_duration(value: Any) -> Any:
    if _is_nan(value):
        return value

    if isinstance(value, (int, float)):
        return int(value)

    if isinstance(value, str):
        text = value.strip()
        if not text:
            return value
        parts = text.split(":")
        if len(parts) == 3 and all(part.isdigit() for part in parts):
            hours, minutes, seconds = (int(part) for part in parts)
            if 0 <= minutes < 60 and 0 <= seconds < 60:
                return hours * 3600 + minutes * 60 + seconds
        elif len(parts) == 2 and all(part.isdigit() for part in parts):
            minutes, seconds = (int(part) for part in parts)
            if 0 <= seconds < 60:
                return minutes * 60 + seconds
        else:
            try:
                return int(float(text))
            except (TypeError, ValueError):
                return value

    return value


def to_array(value: Any) -> list[Any]:
    if _is_nan(value):
        return []

    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)

    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []

        parsed = _safe_literal_eval(text)
        if isinstance(parsed, (list, tuple)):
            return list(parsed)

        normalized = (
            text.replace("null", "None")
            .replace("true", "True")
            .replace("false", "False")
        )
        parsed = _safe_literal_eval(normalized)
        if isinstance(parsed, (list, tuple)):
            return list(parsed)

        parts = [part.strip() for part in text.split(",")]
        return [part for part in parts if part]

    return [value]


STANDARDISERS: dict[str, StandardisationFn] = {
    "toLowerCase": to_lower_case,
    "toUpperCase": to_upper_case,
    "trimSpaces": trim_spaces,
    "parseDate": parse_date,
    "normalizeDuration": normalize_duration,
    "toArray": to_array,
    "extract_genre_ids": extract_genre_ids,
    "normalize_tags": normalize_tags,
}

__all__ = [
    "STANDARDISERS",
    "StandardisationFn",
    "extract_genre_ids",
    "normalize_tags",
    "to_lower_case",
    "to_upper_case",
    "trim_spaces",
    "parse_date",
    "normalize_duration",
    "to_array",
]
