"""Daily ingestion: both Open-Meteo APIs, every city, into DuckDB.

Usage:  python ingest.py
"""

import os
import sys

import duckdb
import pandas as pd
import pandera.errors
from dotenv import load_dotenv

from ingestion.load import create_tables, load_cities, upsert
from ingestion.open_meteo import (
    AIR_URL,
    AIR_VARIABLES,
    WEATHER_URL,
    WEATHER_VARIABLES,
    fetch,
    to_frame,
)
from ingestion.schemas import AIR_QUALITY, WEATHER

CITIES_PATH = "data/cities.csv"


def collect(cities, url, variables, fetcher):
    """Call the API once per city and stack the answers."""
    frames = []
    for row in cities.itertuples():
        payload = fetcher(url, row.latitude, row.longitude, variables)
        frames.append(to_frame(payload, row.city, variables))
    return pd.concat(frames, ignore_index=True)


def run(db_path, cities_path=CITIES_PATH, fetcher=fetch):
    cities = pd.read_csv(cities_path)
    air = collect(cities, AIR_URL, AIR_VARIABLES, fetcher)
    weather = collect(cities, WEATHER_URL, WEATHER_VARIABLES, fetcher)

    # Refuse the whole load if one answer looks wrong: nothing is written.
    air = AIR_QUALITY.validate(air, lazy=True)
    weather = WEATHER.validate(weather, lazy=True)

    con = duckdb.connect(db_path)
    try:
        create_tables(con)
        load_cities(con, cities)
        air_rows = upsert(con, "air_quality", air)
        weather_rows = upsert(con, "weather", weather)
    finally:
        con.close()

    print(f"Received {len(air)} air quality rows, raw.air_quality now has {air_rows} rows")
    print(f"Received {len(weather)} weather rows, raw.weather now has {weather_rows} rows")
    return air_rows, weather_rows


if __name__ == "__main__":
    load_dotenv()
    try:
        run(os.getenv("DUCKDB_PATH", "warehouse.duckdb"))
    except pandera.errors.SchemaErrors as error:
        print("REFUSED: an API answer does not match the expected schema")
        print(error.failure_cases[["column", "check", "failure_case"]].to_string(index=False))
        sys.exit(1)
