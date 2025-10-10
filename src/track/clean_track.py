import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Any

HERE = Path(__file__).parent
CSV = "tracks.csv"
CSV_PATH = (HERE / "../../data" / CSV).resolve()

print("Loading track data from:", CSV_PATH)

globalRuleDict = {CSV: {
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
    "track_date_recorded": ["notNull", "validRecordDate", "date"],
    "track_composer": ["string"],
    "track_lyricist": ["string"],
    "track_publisher": ["string"],
    "album_id": ["notNull", "notNegative", "int"],
    "artist_id": ["notNull", "notNegative", "int"]
}}


def convert_to_int(value: Any) -> Any:
    if pd.isna(value):
        return value
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return np.nan


def convert_to_float(value: Any) -> Any:
    if pd.isna(value):
        return value
    try:
        return float(value)
    except (ValueError, TypeError):
        return np.nan


def convert_to_string(value: Any) -> Any:
    if pd.isna(value):
        return value
    return str(value)


def convert_to_date(value: Any) -> Any:
    if pd.isna(value):
        return value
    try:
        if isinstance(value, str):
            dt = pd.to_datetime(value)
        else:
            dt = pd.to_datetime(value)
        return dt.strftime('%Y-%m-%d')
    except (ValueError, TypeError):
        return np.nan


def convert_to_boolean(value: Any) -> Any:
    if pd.isna(value):
        return value
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ['true', '1', 'yes']
    return bool(value)


def is_not_null(value: Any) -> bool:
    return not pd.isna(value)


def is_not_negative(value: Any) -> bool:
    if pd.isna(value):
        return True
    try:
        return float(value) >= 0
    except (ValueError, TypeError):
        return False


def is_lower_case(value: Any) -> bool:
    if pd.isna(value):
        return True
    return isinstance(value, str) and value == value.lower()


def is_upper_case(value: Any) -> bool:
    if pd.isna(value):
        return True
    return isinstance(value, str) and value == value.upper()


def is_before_now(value: Any) -> bool:
    if pd.isna(value):
        return True
    try:
        dt = pd.to_datetime(value)
        return dt < pd.Timestamp.now()
    except (ValueError, TypeError):
        return False


def is_after_now(value: Any) -> bool:
    if pd.isna(value):
        return True
    try:
        dt = pd.to_datetime(value)
        return dt > pd.Timestamp.now()
    except (ValueError, TypeError):
        return False


def is_valid_record_date(value: Any, row: pd.Series) -> bool:
    if pd.isna(value):
        return True
    try:
        record_date = pd.to_datetime(value)
        created_date = pd.to_datetime(row['track_date_created'])
        now = pd.Timestamp.now()
        return record_date < created_date and created_date < now
    except (ValueError, TypeError, KeyError):
        return False


def respect_rule(value: Any, rule: str, row: pd.Series = None) -> bool:
    if rule == "notNull":
        return is_not_null(value)
    elif rule == "notNegative":
        return is_not_negative(value)
    elif rule == "toLowerCase":
        return is_lower_case(value)
    elif rule == "toUpperCase":
        return is_upper_case(value)
    elif rule == "beforeNow":
        return is_before_now(value)
    elif rule == "afterNow":
        return is_after_now(value)
    elif rule == "validRecordDate":
        return is_valid_record_date(value, row)
    elif rule in ["int", "float", "string", "date", "boolean", "array"]:
        return True
    else:
        return True


def is_value_valid(value: Any, global_rules: list, row: pd.Series = None) -> bool:
    for rule in global_rules:
        if not respect_rule(value, rule, row):
            return False
    return True


def convert_value(value: Any, rules: list) -> Any:
    if "int" in rules:
        value = convert_to_int(value)
    elif "float" in rules:
        value = convert_to_float(value)
    elif "date" in rules:
        value = convert_to_date(value)
    elif "boolean" in rules:
        value = convert_to_boolean(value)
    elif "string" in rules:
        value = convert_to_string(value)
    return value


def clean_csv(csv_path: str, global_rules: dict) -> None:
    csv_name = Path(csv_path).name
    
    if csv_name not in global_rules:
        print(f"No rules found for {csv_name}")
        return
    
    df = pd.read_csv(csv_path)
    rules = global_rules[csv_name]
    
    df = df[[col for col in df.columns if col in rules]]
    
    for col in df.columns:
        if col in rules:
            df[col] = df[col].apply(lambda x: convert_value(x, rules[col]))
    
    valid_rows = []
    for idx, row in df.iterrows():
        is_valid = True
        for col in df.columns:
            if col in rules:
                if not is_value_valid(row[col], rules[col], row):
                    is_valid = False
                    break
        if is_valid:
            valid_rows.append(idx)
    
    df_clean = df.loc[valid_rows]
    
    output_path = HERE / f"clean_{csv_name}"
    df_clean.to_csv(output_path, index=False)
    print(f"Cleaned CSV saved to: {output_path}")
    print(f"Rows: {len(df)} -> {len(df_clean)} (removed {len(df) - len(df_clean)})")


if __name__ == "__main__":
    clean_csv(CSV_PATH, globalRuleDict)

