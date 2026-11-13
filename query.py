"""Run one SQL query on the warehouse and print the result.

Usage:  python query.py "select count(*) from raw.air_quality"
"""

import sys

import duckdb

con = duckdb.connect("warehouse.duckdb", read_only=True)
con.sql(sys.argv[1]).show()
