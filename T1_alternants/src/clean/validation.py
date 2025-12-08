from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Literal, Sequence, cast

import numpy as np
import pandas as pd
from standardisation import STANDARDISERS

@dataclass
class CleanReport:
    csv_name: str
    output_path: Path | None
    original_rows: int
    filtered_rows: int
    cleaned_rows: int
    removed_rows: int
    retention_percentage: float
    rule_failures: dict[str, int] = field(default_factory=dict)
    missing_columns: list[str] = field(default_factory=list)
    messages: list[str] = field(default_factory=list)
    applied_standardisations: dict[str, list[str]] = field(default_factory=dict)

    @property
    def skipped(self) -> bool:
        return self.output_path is None


def _flatten_columns(dataframe: pd.DataFrame) -> None:
    if isinstance(dataframe.columns, pd.MultiIndex):
        flattened: list[str] = []
        for col in dataframe.columns.values:
            parts = [str(part) for part in col if str(part) != "nan"]
            name = "_".join(parts).strip("_")
            flattened.append(name)
        dataframe.columns = flattened
    else:
        dataframe.columns = [str(col) for col in dataframe.columns]

    dataframe.columns = [
        col.replace("Unnamed: 0_", "").strip("_") for col in dataframe.columns
    ]


def _load_dataframe(
    csv_path: Path, header_rows: Sequence[int] | int | Literal["infer"] | None
) -> pd.DataFrame:
    dataframe = pd.read_csv(csv_path, header=header_rows, low_memory=False)
    _flatten_columns(dataframe)
    return dataframe


def _convert_to_int(value: Any) -> Any:
    if _is_nan(value):
        return value
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return np.nan


def _convert_to_float(value: Any) -> Any:
    if _is_nan(value):
        return value
    try:
        return float(value)
    except (ValueError, TypeError):
        return np.nan


def _convert_to_string(value: Any) -> Any:
    if _is_nan(value):
        return value
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=True)
    if isinstance(value, (list, tuple, set, np.ndarray, pd.Series)):
        return json.dumps(list(value), ensure_ascii=True)
    return str(value)


def _convert_to_date(value: Any) -> Any:
    if _is_nan(value):
        return value
    try:
        timestamp = pd.to_datetime(value)
        return timestamp.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return np.nan


def _convert_to_boolean(value: Any) -> Any:
    if _is_nan(value):
        return value
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in {"true", "1", "yes"}
    return bool(value)

def _r_is_true(value: Any, _: pd.Series | None = None) -> bool:
    if _is_nan(value):
        return False
    boolean_value = _convert_to_boolean(value)
    if isinstance (boolean_value, bool):
        return boolean_value
    else:
        return False

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


def _to_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_datetime_utc(value: Any) -> pd.Timestamp | None:
    timestamp = pd.to_datetime(value, errors="coerce", utc=True)
    return None if pd.isna(timestamp) else timestamp


def _now_utc() -> pd.Timestamp:
    return pd.Timestamp.now(tz="UTC")

_NOW_UTC: Callable[[], pd.Timestamp] = _now_utc


ValidationRuleFn = Callable[[Any, pd.Series | None], bool]


def _r_not_null(value: Any, _: pd.Series | None = None) -> bool:
    return not _is_nan(value)


def _r_not_negative(value: Any, _: pd.Series | None = None) -> bool:
    if _is_nan(value):
        return True
    numeric_value = _to_float(value)
    return numeric_value is not None and numeric_value >= 0


def _r_positive_number(value: Any, _: pd.Series | None = None) -> bool:
    if _is_nan(value):
        return True
    numeric_value = _to_float(value)
    return numeric_value is not None and numeric_value > 0


def _r_to_lower_case(value: Any, _: pd.Series | None = None) -> bool:
    return _is_nan(value) or (isinstance(value, str) and value == value.lower())


def _r_to_upper_case(value: Any, _: pd.Series | None = None) -> bool:
    return _is_nan(value) or (isinstance(value, str) and value == value.upper())


def _r_before_now(value: Any, _: pd.Series | None = None) -> bool:
    if _is_nan(value):
        return True
    timestamp = _to_datetime_utc(value)
    return timestamp is not None and timestamp < _NOW_UTC()


def _r_after_now(value: Any, _: pd.Series | None = None) -> bool:
    if _is_nan(value):
        return True
    timestamp = _to_datetime_utc(value)
    return timestamp is not None and timestamp > _NOW_UTC()


def _r_is_int(value: Any, _: pd.Series | None = None) -> bool:
    if _is_nan(value):
        return True
    numeric_value = _to_float(value)
    return numeric_value is not None and float(numeric_value).is_integer()


def _r_is_float(value: Any, _: pd.Series | None = None) -> bool:
    if _is_nan(value):
        return True
    return _to_float(value) is not None


def _r_is_double(value: Any, _: pd.Series | None = None) -> bool:
    if _is_nan(value):
        return True
    return _to_float(value) is not None


def _r_is_string(value: Any, _: pd.Series | None = None) -> bool:
    return _is_nan(value) or isinstance(value, str)


def _r_is_date(value: Any, _: pd.Series | None = None) -> bool:
    if _is_nan(value):
        return True
    return _to_datetime_utc(value) is not None


def _r_is_boolean(value: Any, _: pd.Series | None = None) -> bool:
    return _is_nan(value) or isinstance(value, (bool, np.bool_))


def _r_is_array(value: Any, _: pd.Series | None = None) -> bool:
    if _is_nan(value):
        return True
    if isinstance(value, (list, tuple)):
        return True
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return False
        try:
            parsed = json.loads(text)
        except (TypeError, ValueError):
            return False
        return isinstance(parsed, list)
    return False


VALIDATION_RULES: dict[str, ValidationRuleFn] = {
    "notNull": _r_not_null,
    "notNegative": _r_not_negative,
    "positiveNumber": _r_positive_number,
    "toLowerCase": _r_to_lower_case,
    "toUpperCase": _r_to_upper_case,
    "beforeNow": _r_before_now,
    "afterNow": _r_after_now,
    "isTrue": _r_is_true,
    "int": _r_is_int,
    "float": _r_is_float,
    "double": _r_is_double,
    "string": _r_is_string,
    "date": _r_is_date,
    "boolean": _r_is_boolean,
    "array": _r_is_array,
}


def _respect_rule(
    value: Any,
    rule: str,
    column: str,
    row_index: int,
    row: pd.Series | None = None,
    *,
    duplicates: dict[str, pd.Series] | None = None,
) -> bool:
    if rule == "unique":
        if duplicates is None:
            return True
        duplicate_flags = duplicates.get(column)
        if duplicate_flags is None:
            return True
        try:
            is_duplicate = bool(duplicate_flags.iloc[row_index])
        except IndexError:
            return True
        return not is_duplicate

    rule_fn = VALIDATION_RULES.get(rule)
    if rule_fn is None:
        return True
    return rule_fn(value, row)


def _convert_value(value: Any, rules: list[str]) -> Any:
    if "int" in rules:
        return _convert_to_int(value)
    if "double" in rules:
        return _convert_to_float(value)
    if "float" in rules:
        return _convert_to_float(value)
    if "date" in rules:
        return _convert_to_date(value)
    if "boolean" in rules:
        return _convert_to_boolean(value)
    if "string" in rules:
        return _convert_to_string(value)
    return value


def _validate_dataframe(
    dataframe: pd.DataFrame, validation_rules: dict[str, list[str]]
) -> tuple[list[int], dict[str, int]]:
    valid_indices: list[int] = []
    rule_failure_stats: dict[str, int] = {}

    duplicates_by_column: dict[str, pd.Series] = {}
    for column, rules in validation_rules.items():
        if column in dataframe.columns and "unique" in rules:
            duplicates_by_column[column] = dataframe[column].duplicated(keep=False)

    for row_index, row in dataframe.iterrows():
        row_is_valid = True

        for column, rules in validation_rules.items():
            if column not in dataframe.columns:
                continue

            value = row[column]

            for rule in rules:
                if not _respect_rule(
                    value,
                    rule,
                    column,
                    cast(int, row_index),
                    row,
                    duplicates=duplicates_by_column,
                ):
                    row_is_valid = False
                    rule_key = f"{column}:{rule}"
                    rule_failure_stats[rule_key] = rule_failure_stats.get(rule_key, 0) + 1
                    break

            if not row_is_valid:
                break

        if row_is_valid:
            valid_indices.append(cast(int, row_index))

    return valid_indices, rule_failure_stats


def clean_csv(
    csv_path: Path,
    config: dict[str, Any],
    output_dir: Path,
    *,
    limit: int | None = None,
) -> CleanReport:
    validation_rules_config: dict[str, list[str]] = config.get("validation_rules", {})
    standardisation_rules_config: dict[str, list[str]] = config.get("standardisation_rules", {})
    csv_name = csv_path.name

    header_rows = cast(Sequence[int] | int | Literal["infer"] | None, config.get("header_rows"))
    dataframe = _load_dataframe(csv_path, header_rows)
    original_row_count = len(dataframe)

    if rename_map := config.get("rename_columns"):
        dataframe = dataframe.rename(columns=rename_map)

    if skip_rows := config.get("skip_rows"):
        dataframe = dataframe.drop(index=skip_rows, errors="ignore")

    dataframe = dataframe.reset_index(drop=True)

    pre_limit_count = len(dataframe)

    if limit is not None and limit >= 0:
        dataframe = dataframe.iloc[:limit]

    default_validation_rules = validation_rules_config.get("__all__", [])
    specific_validation_rules = {
        column: rules for column, rules in validation_rules_config.items() if column != "__all__"
    }

    default_standardisers = standardisation_rules_config.get("__all__", [])
    specific_standardisers = {
        column: rules for column, rules in standardisation_rules_config.items() if column != "__all__"
    }

    missing_columns = [
        col for col in specific_validation_rules.keys() if col not in dataframe.columns
    ]

    if default_validation_rules:
        selected_columns = list(dataframe.columns)
    else:
        selected_columns = [col for col in dataframe.columns if col in specific_validation_rules]

    effective_validation_rules: dict[str, list[str]] = {}
    for column in selected_columns:
        if column in specific_validation_rules:
            effective_validation_rules[column] = specific_validation_rules[column]
        elif default_validation_rules:
            effective_validation_rules[column] = default_validation_rules

    dataframe = dataframe[selected_columns]
    filtered_row_count = len(dataframe)

    applied_standardisations: dict[str, list[str]] = {}
    effective_standardisers: dict[str, list[str]] = {}
    for column in dataframe.columns:
        if column in specific_standardisers:
            effective_standardisers[column] = specific_standardisers[column]
        elif default_standardisers:
            effective_standardisers[column] = default_standardisers

    for column, standardisers in effective_standardisers.items():
        rule_sequence = list(standardisers)
        for rule_name in rule_sequence:
            standardise = STANDARDISERS.get(rule_name)
            if standardise is None:
                continue
            dataframe[column] = dataframe[column].apply(standardise)
            applied_standardisations.setdefault(column, []).append(rule_name)

    if not effective_validation_rules:
        return CleanReport(
            csv_name=csv_name,
            output_path=None,
            original_rows=original_row_count,
            filtered_rows=filtered_row_count,
            cleaned_rows=0,
            removed_rows=filtered_row_count,
            retention_percentage=0.0,
            missing_columns=missing_columns,
            messages=["No columns matched the rule configuration; skipping export."],
        )

    for column, rules in effective_validation_rules.items():
        dataframe.loc[:, column] = dataframe[column].apply(lambda value: _convert_value(value, rules))

    valid_indices, rule_failures = _validate_dataframe(dataframe, effective_validation_rules)
    cleaned_dataframe = dataframe.loc[valid_indices].copy()

    for column, rules in effective_validation_rules.items():
        if column not in cleaned_dataframe.columns:
            continue
        if "int" in rules:
            cleaned_dataframe[column] = pd.to_numeric(
                cleaned_dataframe[column], errors="coerce"
            ).astype("Int64")
        elif "float" in rules:
            cleaned_dataframe[column] = pd.to_numeric(
                cleaned_dataframe[column], errors="coerce"
            )
        elif "boolean" in rules:
            cleaned_dataframe[column] = cleaned_dataframe[column].astype(bool)

    cleaned_row_count = len(cleaned_dataframe)
    removed_row_count = filtered_row_count - cleaned_row_count
    retention_percentage = (
        (cleaned_row_count / filtered_row_count) * 100 if filtered_row_count > 0 else 0.0
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"clean_{csv_name}"
    cleaned_dataframe.to_csv(output_path, index=False)

    message_lines: list[str] = []
    if limit is not None and limit >= 0 and pre_limit_count > limit:
        message_lines.append(
            f"Processing limited to first {limit} rows (pre-limit rows: {pre_limit_count})."
        )
    if missing_columns:
        message_lines.append(
            f"Missing columns for {csv_name}: {', '.join(sorted(missing_columns))}"
        )

    return CleanReport(
        csv_name=csv_name,
        output_path=output_path,
        original_rows=original_row_count,
        filtered_rows=filtered_row_count,
        cleaned_rows=cleaned_row_count,
        removed_rows=removed_row_count,
        retention_percentage=retention_percentage,
        rule_failures=rule_failures,
        missing_columns=missing_columns,
        messages=message_lines,
        applied_standardisations=applied_standardisations,
    )


__all__ = ["CleanReport", "clean_csv"]
