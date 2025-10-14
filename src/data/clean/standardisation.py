from __future__ import annotations

import ast
import json
from typing import Any, Callable

import pandas as pd
import numpy as np

StandardisationFn = Callable[[Any], Any]


def _is_nan(value: Any) -> bool:
    if isinstance(value, (list, tuple, dict, set, np.ndarray)):
        return False
    try:
        result = pd.isna(value)
    except TypeError:
        return False
    if isinstance(result, (list, tuple, np.ndarray, pd.Series)):
        return False
    return bool(result)


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
            continue

        if isinstance(item, dict):
            # use common keys if present
            candidate = item.get("name") or item.get("tag") or item.get("value")
            if isinstance(candidate, str):
                text = candidate.strip()
                if text:
                    cleaned.append(text)
    return cleaned


def normalize_boolean(value: Any) -> bool:
    return to_boolean(value)


def _normalize_json_scalar(value: Any) -> Any:
    if _is_nan(value):
        return None
    if isinstance(value, bool):
        return bool(value)
    if isinstance(value, (int, np.integer)):
        return int(value)
    if isinstance(value, (float, np.floating)):
        numeric = float(value)
        if np.isnan(numeric):
            return None
        if numeric.is_integer():
            return int(numeric)
        return numeric
    text = str(value).strip()
    if not text:
        return None
    return text


def to_array(value: Any) -> Any:
    if _is_nan(value):
        return value

    sequence = _coerce_sequence(value)
    if sequence is None:
        item = _normalize_json_scalar(value)
        if item is None:
            return json.dumps([], ensure_ascii=True)
        return json.dumps([item], ensure_ascii=True)

    normalised_items: list[Any] = []
    for item in sequence:
        normalised = _normalize_json_scalar(item)
        if normalised is not None:
            normalised_items.append(normalised)

    return json.dumps(normalised_items, ensure_ascii=True)


def to_int(value: Any) -> Any:
    if _is_nan(value):
        return value

    if isinstance(value, bool):
        return int(value)

    if isinstance(value, (int, np.integer)):
        return int(value)

    if isinstance(value, (float, np.floating)):
        numeric = float(value)
        if numeric.is_integer():
            return int(numeric)
        return value

    if isinstance(value, str):
        text = value.strip()
        if not text:
            return value
        sign = ""
        if text[0] in "+-":
            sign = text[0]
            text = text[1:]
        cleaned = (
            text.replace("\u202f", "")
            .replace(" ", "")
            .replace("_", "")
        )
        if not cleaned:
            return value

        if "." in cleaned:
            try:
                numeric = float(f"{sign}{cleaned}")
            except ValueError:
                return value
            if numeric.is_integer():
                return int(numeric)
            return value

        if "," in cleaned:
            parts = cleaned.split(",")
            if not all(part.isdigit() for part in parts):
                return value
            if all(len(part) == 3 for part in parts[1:]):
                candidate = f"{sign}{''.join(parts)}"
                try:
                    return int(candidate)
                except ValueError:
                    return value
            try:
                numeric = float(f"{sign}{'.'.join(parts)}")
            except ValueError:
                return value
            if numeric.is_integer():
                return int(numeric)
            return value

        candidate = f"{sign}{cleaned}"
        if candidate.lstrip("-+").isdigit():
            try:
                return int(candidate)
            except ValueError:
                return value
        return value

    try:
        numeric = int(value)
    except (TypeError, ValueError):
        return value
    return numeric


def _normalize_decimal_text(text: str) -> str:
    normalized = (
        text.replace("\u202f", "")
        .replace(" ", "")
        .replace("_", "")
    )
    if not normalized:
        return normalized

    sign = ""
    if normalized[0] in "+-":
        sign = normalized[0]
        normalized = normalized[1:]

    if "," in normalized and "." in normalized:
        normalized = normalized.replace(",", "")
    elif "," in normalized:
        normalized = normalized.replace(",", ".")

    return f"{sign}{normalized}"


def to_float(value: Any) -> Any:
    if _is_nan(value):
        return value

    if isinstance(value, bool):
        return float(int(value))

    if isinstance(value, (int, np.integer, float, np.floating)):
        return float(value)

    if isinstance(value, str):
        text = value.strip()
        if not text:
            return value
        normalized = _normalize_decimal_text(text)
        try:
            return float(normalized)
        except ValueError:
            return value

    try:
        return float(value)
    except (TypeError, ValueError):
        return value


def to_double(value: Any) -> Any:
    return to_float(value)


def to_string(value: Any) -> Any:
    if _is_nan(value):
        return value

    if isinstance(value, str):
        text = value.strip()
    else:
        text = str(value)

    escaped = text.replace('"', '\\"')
    return f"\"{escaped}\""


def to_boolean(value: Any) -> Any:
    if _is_nan(value):
        return value

    if isinstance(value, bool):
        return value

    if isinstance(value, (int, np.integer)):
        return bool(int(value))

    if isinstance(value, (float, np.floating)):
        numeric = float(value)
        if np.isnan(numeric):
            return value
        return bool(numeric)

    if isinstance(value, str):
        text = value.strip().lower()
        if text in {"true", "1", "yes", "y"}:
            return True
        if text in {"false", "0", "no", "n"}:
            return False
        return value

    return value


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


STANDARDISERS: dict[str, StandardisationFn] = {
    "toLowerCase": to_lower_case,
    "toUpperCase": to_upper_case,
    "trimSpaces": trim_spaces,
    "parseDate": parse_date,
    "normalizeDuration": normalize_duration,
    "extractGenreIds": extract_genre_ids,
    "normalizeTags": normalize_tags,
    "normalizeBoolean": normalize_boolean,
    "toArray": to_array,
    "toInt": to_int,
    "toFloat": to_float,
    "toDouble": to_double,
    "toString": to_string,
    "toBoolean": to_boolean,
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
    "normalize_boolean",
    "to_int",
    "to_float",
    "to_double",
    "to_string",
    "to_boolean",
]
