import pandas as pd
import numpy as np
from pathlib import Path
from typing import Any

HERE = Path(__file__).parent
OUTPUT_DIR = HERE / "out"
CSV_FILENAME = "tracks.csv"
CSV_PATH = (HERE / "../../data" / CSV_FILENAME).resolve()

RULES_BY_CSV = {
    CSV_FILENAME: {
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
    }
}


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


def is_value_valid(value: Any, rules: list, row: pd.Series = None) -> bool:
    for rule in rules:
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


def clean_csv(csv_path: str, rules_by_csv: dict) -> None:
    csv_filename = Path(csv_path).name
    
    if csv_filename not in rules_by_csv:
        print(f"No rules found for {csv_filename}")
        return
    
    dataframe = pd.read_csv(csv_path, header=[0, 1])
    dataframe.columns = ['_'.join(col).strip('_') for col in dataframe.columns.values]
    dataframe = dataframe.rename(columns=lambda x: x.replace('Unnamed: 0_', ''))
    
    if 'level_0_level_1' in dataframe.columns:
        first_cell_value = dataframe.iloc[0, 0]
        if first_cell_value == 'track_id':
            dataframe = dataframe.rename(columns={'level_0_level_1': 'track_id'})
            dataframe = dataframe[1:]
    
    column_rules = rules_by_csv[csv_filename]
    
    dataframe = dataframe[[col for col in dataframe.columns if col in column_rules]]
    
    for column in dataframe.columns:
        if column in column_rules:
            dataframe[column] = dataframe[column].apply(lambda x: convert_value(x, column_rules[column]))
    
    valid_row_indices = []
    for row_index, row in dataframe.iterrows():
        row_is_valid = True
        for column in dataframe.columns:
            if column in column_rules:
                if not is_value_valid(row[column], column_rules[column], row):
                    row_is_valid = False
                    break
        if row_is_valid:
            valid_row_indices.append(row_index)
    
    cleaned_dataframe = dataframe.loc[valid_row_indices]
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    output_path = OUTPUT_DIR / f"clean_{csv_filename}"
    cleaned_dataframe.to_csv(output_path, index=False)
    print(f"Cleaned CSV saved to: {output_path}")
    print(f"Rows: {len(dataframe)} -> {len(cleaned_dataframe)} (removed {len(dataframe) - len(cleaned_dataframe)})")


if __name__ == "__main__":
    print(f"Loading track data from: {CSV_PATH}")
    clean_csv(CSV_PATH, RULES_BY_CSV)

