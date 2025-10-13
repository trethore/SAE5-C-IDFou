from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import numpy as np
import pandas as pd

@dataclass
class CleanReport:
    csv_name: str
    output_path: Path | None
    original_rows: int
    filtered_rows: int
    cleaned_rows: int
    removed_rows: int
    retention_percentage: float
    rule_failures: Dict[str, int] = field(default_factory=dict)
    missing_columns: List[str] = field(default_factory=list)
    messages: List[str] = field(default_factory=list)

    @property
    def skipped(self) -> bool:
        return self.output_path is None


def _flatten_columns(dataframe: pd.DataFrame) -> None:
    if isinstance(dataframe.columns, pd.MultiIndex):
        flattened: List[str] = []
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


def _load_dataframe(csv_path: Path, header_rows: Iterable[int] | int | None) -> pd.DataFrame:
    dataframe = pd.read_csv(csv_path, header=header_rows)
    _flatten_columns(dataframe)
    return dataframe


def _convert_to_int(value: Any) -> Any:
    if pd.isna(value):
        return value
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return np.nan


def _convert_to_float(value: Any) -> Any:
    if pd.isna(value):
        return value
    try:
        return float(value)
    except (ValueError, TypeError):
        return np.nan


def _convert_to_string(value: Any) -> Any:
    if pd.isna(value):
        return value
    return str(value)


def _convert_to_date(value: Any) -> Any:
    if pd.isna(value):
        return value
    try:
        timestamp = pd.to_datetime(value)
        return timestamp.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return np.nan


def _convert_to_boolean(value: Any) -> Any:
    if pd.isna(value):
        return value
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in {"true", "1", "yes"}
    return bool(value)


def _respect_rule(value: Any, rule: str, row: pd.Series | None = None) -> bool:
    if rule == "notNull":
        return not pd.isna(value)
    if rule == "notNegative":
        if pd.isna(value):
            return True
        try:
            return float(value) >= 0
        except (ValueError, TypeError):
            return False
    if rule == "toLowerCase":
        return pd.isna(value) or (isinstance(value, str) and value == value.lower())
    if rule == "toUpperCase":
        return pd.isna(value) or (isinstance(value, str) and value == value.upper())
    if rule == "beforeNow":
        if pd.isna(value):
            return True
        try:
            return pd.to_datetime(value) < pd.Timestamp.now()
        except (ValueError, TypeError):
            return False
    if rule == "afterNow":
        if pd.isna(value):
            return True
        try:
            return pd.to_datetime(value) > pd.Timestamp.now()
        except (ValueError, TypeError):
            return False
    if rule in {"int", "float", "string", "date", "boolean", "array"}:
        return True
    return True


def _convert_value(value: Any, rules: List[str]) -> Any:
    if "int" in rules:
        return _convert_to_int(value)
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
    dataframe: pd.DataFrame, column_rules: Dict[str, List[str]]
) -> Tuple[List[int], Dict[str, int]]:
    valid_indices: List[int] = []
    rule_failure_stats: Dict[str, int] = {}

    for row_index, row in dataframe.iterrows():
        row_is_valid = True

        for column, rules in column_rules.items():
            if column not in dataframe.columns:
                continue

            value = row[column]

            for rule in rules:
                if not _respect_rule(value, rule, row):
                    row_is_valid = False
                    rule_key = f"{column}:{rule}"
                    rule_failure_stats[rule_key] = rule_failure_stats.get(rule_key, 0) + 1
                    break

            if not row_is_valid:
                break

        if row_is_valid:
            valid_indices.append(row_index)

    return valid_indices, rule_failure_stats


def clean_csv(csv_path: Path, config: Dict[str, Any], output_dir: Path) -> CleanReport:
    column_rules: Dict[str, List[str]] = config.get("column_rules", {})
    csv_name = csv_path.name

    dataframe = _load_dataframe(csv_path, config.get("header_rows"))
    original_row_count = len(dataframe)

    if rename_map := config.get("rename_columns"):
        dataframe = dataframe.rename(columns=rename_map)

    if skip_rows := config.get("skip_rows"):
        dataframe = dataframe.drop(index=skip_rows, errors="ignore")

    dataframe = dataframe.reset_index(drop=True)

    missing_columns = [col for col in column_rules.keys() if col not in dataframe.columns]

    selected_columns = [col for col in dataframe.columns if col in column_rules]
    dataframe = dataframe[selected_columns]
    filtered_row_count = len(dataframe)

    if not selected_columns:
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

    for column in selected_columns:
        rules = column_rules[column]
        dataframe.loc[:, column] = dataframe[column].apply(lambda value: _convert_value(value, rules))

    valid_indices, rule_failures = _validate_dataframe(dataframe, column_rules)
    cleaned_dataframe = dataframe.loc[valid_indices]

    cleaned_row_count = len(cleaned_dataframe)
    removed_row_count = filtered_row_count - cleaned_row_count
    retention_percentage = (
        (cleaned_row_count / filtered_row_count) * 100 if filtered_row_count > 0 else 0.0
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"clean_{csv_name}"
    cleaned_dataframe.to_csv(output_path, index=False)

    message_lines: List[str] = []
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
    )


__all__ = ["CleanReport", "clean_csv"]

