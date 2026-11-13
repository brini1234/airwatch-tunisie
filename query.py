"""Run one SQL query on the warehouse and print the result.

Usage:
    python query.py "select count(*) from raw.air_quality"
    python query.py --md "select ..."     prints a Markdown table (for the CI summary)
"""

import os
import sys

import duckdb

args = [arg for arg in sys.argv[1:] if arg != "--md"]
con = duckdb.connect(os.getenv("DUCKDB_PATH", "warehouse.duckdb"), read_only=True)
result = con.sql(args[0])

if "--md" in sys.argv:
    print("| " + " | ".join(result.columns) + " |")
    print("|" + " --- |" * len(result.columns))
    for row in result.fetchall():
        print("| " + " | ".join(str(value) for value in row) + " |")
else:
    result.show()
