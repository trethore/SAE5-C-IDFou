import os
import psycopg2

from dotenv import load_dotenv
from typing import cast
from ast import literal_eval

from local_types import pref_type
from consts import (
    multi_values,
    pref_to_vec_map,
)


def main() -> None:
    load_dotenv()

    connection = psycopg2.connect(
        host="localhost",
        port=os.environ["PGDB_PORT"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_ROOT_PASSWORD"],
    )

    cursor = connection.cursor()
    cursor.execute(
        "SELECT column_name, data_type, ordinal_position "
        "FROM information_schema.columns "
        "WHERE table_name = 'preference' "
        "ORDER BY ordinal_position; "
    )
    prefs_columns: list[tuple[str, str, int]] = cursor.fetchall()

    cursor.execute("DELETE FROM preference_vector;")

    cursor.execute("SELECT * FROM preference;")
    prefs: list[pref_type] = cursor.fetchall()

    for pref in prefs:
        vector: list[float] = create_vector(pref, prefs_columns)
        cursor.execute(
            "INSERT INTO preference_vector (account_id, embedding) VALUES (%s, %s)",
            (pref[0], vector),
        )

    connection.commit()


def create_vector(pref: pref_type, column: list[tuple[str, str, int]]) -> list[float]:

    def get_i_pref() -> int:
        i_pref: int = 0
        for col in column:
            if col[0] == table_col:
                break
            i_pref += 1
        return i_pref

    def get_values(table_col: str) -> list[str]:
        values: list[str] = []
        if table_col in ["energy_pref"]:
            values = cast(str, pref[i_pref]).split(",  ")
        elif table_col in ["context", "how", "platform", "utility"]:
            values = literal_eval(cast(str, pref[i_pref]))
        return values

    def get_max(table_col: str) -> float:
        result: float = 1.0
        if table_col == "duration_pref":
            result = 11.0
        elif table_col == "age_range":
            result = 6.0
        elif table_col == "frequency":
            result = 2.0
        elif table_col in [
            "when_listening",
            "tempo_pref",
            "quality_pref",
            "curiosity_pref",
        ]:
            result = 4.0
        return result

    vector: list[float] = []

    for vec_item in pref_to_vec_map.keys():
        for table_col in pref_to_vec_map[vec_item].keys():
            val: float
            i_pref = get_i_pref()
            val_to_vec_val = pref_to_vec_map[vec_item][table_col]
            if val_to_vec_val is None:
                val = float(pref[i_pref])
            elif table_col in multi_values:
                values: list[str] = get_values(table_col)
                val = 0.0
                for value in values:
                    if value in val_to_vec_val.keys():
                        val = val_to_vec_val[value]
            else:
                try:
                    val = val_to_vec_val[cast(str, pref[i_pref])]
                except KeyError:
                    val = 0.0
            val /= get_max(table_col)
            vector.append(val)
            # print(
            #     f"{vec_item} {' ' * (30 - len(vec_item))}"
            #     f"{table_col} {' ' * (14 - len(table_col))}"
            #     f"{val}"
            # )

    return vector


if __name__ == "__main__":
    main()
