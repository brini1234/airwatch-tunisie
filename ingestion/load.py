"""Load: write into DuckDB without ever creating duplicates.

Each API call also returns the two previous days, so consecutive loads overlap.
The tables have a primary key (city, time) and we use INSERT OR REPLACE:
an hour already loaded is replaced by its newest value, never added twice.
"""

RAW_TABLES = {
    "air_quality": """
        CREATE TABLE IF NOT EXISTS raw.air_quality (
            city VARCHAR NOT NULL,
            time TIMESTAMP NOT NULL,
            pm2_5 DOUBLE,
            pm10 DOUBLE,
            nitrogen_dioxide DOUBLE,
            ozone DOUBLE,
            dust DOUBLE,
            european_aqi DOUBLE,
            _loaded_at TIMESTAMP NOT NULL,
            PRIMARY KEY (city, time)
        )
    """,
    "weather": """
        CREATE TABLE IF NOT EXISTS raw.weather (
            city VARCHAR NOT NULL,
            time TIMESTAMP NOT NULL,
            temperature_2m DOUBLE,
            relative_humidity_2m DOUBLE,
            precipitation DOUBLE,
            wind_speed_10m DOUBLE,
            wind_direction_10m DOUBLE,
            _loaded_at TIMESTAMP NOT NULL,
            PRIMARY KEY (city, time)
        )
    """,
}


def create_tables(con):
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")
    for ddl in RAW_TABLES.values():
        con.execute(ddl)


def upsert(con, table, frame):
    """Insert new hours, replace hours already there. Returns the table's row count."""
    con.register("incoming", frame)
    columns = ", ".join(frame.columns)
    con.execute(
        f"INSERT OR REPLACE INTO raw.{table} ({columns}, _loaded_at) "
        f"SELECT {columns}, current_timestamp FROM incoming"
    )
    con.unregister("incoming")
    return con.execute(f"SELECT count(*) FROM raw.{table}").fetchall()[0][0]


def load_cities(con, cities):
    con.register("incoming_cities", cities)
    con.execute("CREATE OR REPLACE TABLE raw.cities AS SELECT * FROM incoming_cities")
    con.unregister("incoming_cities")
