#!/usr/bin/env python3


import pandas


RAW_ALBUMS_CSV_PATH: str = "data/raw_albums.csv"

RAW_ALBUMS_RULES: dict[str, dict[str, list[str]]] = {
    "raw_albums": {
        "album_id": ["notNull", "unique", "int", "notNegative"],
        "album_title": ["notNull", "string"],
        "album_type": ["notNull", "string"],
        "album_tracks": ["notNull", "int", "positiveNumber"],
        "album_date_released": ["date", "beforeNow"],
        "album_listens": ["notNull", "int", "notNegative"],
        "album_favorites": ["notNull", "int", "notNegative"],
        "album_comments": ["notNull", "int", "notNegative"],
        "album_producer": ["string"],
        "tags": ["array", "string"],
    }
}


def main() -> None:
    raw_album_df: pandas.DataFrame
    clean_album_df: pandas.DataFrame
    try:
        raw_album_df = pandas.read_csv(RAW_ALBUMS_CSV_PATH)
    except FileNotFoundError:
        print(
            "Error: raw_albums.csv not found. Make sure to run the script from the root of the repository."
        )
        exit(1)
    clean_album_df = clean_columns(raw_album_df)
    format_dates(clean_album_df, ["album_date_released"])
    clean_album_df.to_csv("data/clean_albums.csv")


def clean_columns(raw_album_df: pandas.DataFrame) -> pandas.DataFrame:
    """
    Remove useless columns from raw_albums.csv and format dates to YYYY-MM-DD.
    """
    columns_to_drop: list[str] = []
    for column in raw_album_df.columns:
        if column not in RAW_ALBUMS_RULES["raw_albums"].keys():
            columns_to_drop.append(column)
    return raw_album_df.drop(columns_to_drop, axis=1)


def format_dates(data_frame: pandas.DataFrame, columns: list[str]) -> None:
    """
    Format date from MM/DD/YYYY to YYYY-MM-DD in specified columns.

    Args:
        data_frame (pandas.DataFrame): Dataframe
        columns (list[str]): Columns with dates to convert.
    """
    for column in columns:
        data_frame[column] = pandas.to_datetime(data_frame[column], format="%m/%d/%Y")
        data_frame[column] = data_frame[column].dt.strftime("%Y-%m-%d")


if __name__ == "__main__":
    main()
