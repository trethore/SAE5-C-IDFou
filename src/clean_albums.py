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
    """
    Remove useless columns from raw_albums.csv and format dates to YYYY-MM-DD.
    """
    try:
        raw_album_df: pandas.DataFrame = pandas.read_csv(RAW_ALBUMS_CSV_PATH)
        columns_to_drop: list[str] = []
        for column in raw_album_df.columns:
            if column not in RAW_ALBUMS_RULES["raw_albums"].keys():
                columns_to_drop.append(column)
        clean_album_df: pandas.DataFrame = raw_album_df.drop(columns_to_drop, axis=1)
        clean_album_df["album_date_released"] = pandas.to_datetime(
            clean_album_df["album_date_released"], format="%m/%d/%Y"
        )
        clean_album_df["album_date_released"] = clean_album_df[
            "album_date_released"
        ].dt.strftime("%Y-%m-%d")
        clean_album_df.to_csv("data/clean_albums.csv")
    except FileNotFoundError:
        print(
            "Error: raw_albums.csv not found. Make sure to run the script from the root of the repository."
        )
        exit(1)


if __name__ == "__main__":
    main()
