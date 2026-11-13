"""Unit tests: no network, the API is replaced by a fake answer."""

import duckdb
import pandas as pd
import pandera.errors
import pytest

from ingest import run, run_sample
from ingestion.load import create_tables, upsert
from ingestion.open_meteo import AIR_VARIABLES, WEATHER_VARIABLES, to_frame
from ingestion.schemas import AIR_QUALITY, WEATHER

HOURS = ["2026-11-13T00:00", "2026-11-13T01:00", "2026-11-13T02:00"]


def fake_payload(variables, hours=HOURS, value=10.0):
    return {"hourly": {"time": hours, **{v: [value] * len(hours) for v in variables}}}


def air_frame(value=10.0, hours=HOURS):
    payload = fake_payload(AIR_VARIABLES, hours=hours, value=value)
    return AIR_QUALITY.validate(to_frame(payload, "Tunis", AIR_VARIABLES))


def fake_fetcher(url, latitude, longitude, variables):
    return fake_payload(variables)


def test_to_frame_has_one_row_per_hour():
    frame = to_frame(fake_payload(AIR_VARIABLES), "Tunis", AIR_VARIABLES)
    assert len(frame) == 3
    assert list(frame.columns) == ["city", "time", *AIR_VARIABLES]
    assert (frame["city"] == "Tunis").all()


def test_negative_pollution_is_refused():
    frame = to_frame(fake_payload(AIR_VARIABLES, value=-5.0), "Tunis", AIR_VARIABLES)
    with pytest.raises(pandera.errors.SchemaErrors):
        AIR_QUALITY.validate(frame, lazy=True)


def test_impossible_humidity_is_refused():
    frame = to_frame(fake_payload(WEATHER_VARIABLES, value=150.0), "Sfax", WEATHER_VARIABLES)
    with pytest.raises(pandera.errors.SchemaErrors):
        WEATHER.validate(frame, lazy=True)


def test_missing_value_is_accepted():
    payload = fake_payload(AIR_VARIABLES)
    payload["hourly"]["pm2_5"][0] = None
    frame = AIR_QUALITY.validate(to_frame(payload, "Tunis", AIR_VARIABLES), lazy=True)
    assert frame["pm2_5"].isna().sum() == 1


def test_upsert_twice_creates_no_duplicates():
    con = duckdb.connect()
    create_tables(con)
    assert upsert(con, "air_quality", air_frame()) == 3
    assert upsert(con, "air_quality", air_frame()) == 3


def test_upsert_keeps_the_newest_value():
    con = duckdb.connect()
    create_tables(con)
    upsert(con, "air_quality", air_frame(value=10.0))
    upsert(con, "air_quality", air_frame(value=20.0))
    assert con.execute("SELECT DISTINCT pm2_5 FROM raw.air_quality").fetchall() == [(20.0,)]


def test_overlapping_loads_only_add_new_hours():
    con = duckdb.connect()
    create_tables(con)
    upsert(con, "air_quality", air_frame(hours=HOURS[:2]))
    assert upsert(con, "air_quality", air_frame(hours=HOURS[1:])) == 3


def test_run_twice_end_to_end(tmp_path):
    db = str(tmp_path / "test.duckdb")
    cities = pd.read_csv("data/cities.csv")
    expected = len(cities) * len(HOURS)
    assert run(db, fetcher=fake_fetcher) == (expected, expected)
    assert run(db, fetcher=fake_fetcher) == (expected, expected)


def test_sample_load_twice(tmp_path):
    db = str(tmp_path / "sample.duckdb")
    first = run_sample(db)
    assert run_sample(db) == first
