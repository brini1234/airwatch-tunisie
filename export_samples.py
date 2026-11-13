"""Save the raw tables of the warehouse as the CI sample (run once, after a real ingestion).

Usage:  python export_samples.py
"""

import os

import duckdb

con = duckdb.connect(os.getenv("DUCKDB_PATH", "warehouse.duckdb"), read_only=True)
for table in ["air_quality", "weather"]:
    path = f"tests/fixtures/{table}_sample.csv"
    con.execute(
        f"COPY (SELECT * EXCLUDE (_loaded_at) FROM raw.{table} ORDER BY city, time) "
        f"TO '{path}' (HEADER, DELIMITER ',')"
    )
    rows = con.execute(f"SELECT count(*) FROM raw.{table}").fetchall()[0][0]
    print(f"Wrote {rows} rows to {path}")
