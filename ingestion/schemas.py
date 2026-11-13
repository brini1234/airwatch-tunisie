"""Checks run on every API answer before it is loaded (Pandera, as in TP4)."""

import pandera.pandas as pa


def _between(low, high):
    return pa.Check.in_range(low, high, ignore_na=True)


AIR_QUALITY = pa.DataFrameSchema(
    {
        "city": pa.Column(str),
        "time": pa.Column("datetime64[ns]"),
        "pm2_5": pa.Column(float, _between(0, 1000), nullable=True),
        "pm10": pa.Column(float, _between(0, 5000), nullable=True),
        "nitrogen_dioxide": pa.Column(float, _between(0, 1000), nullable=True),
        "ozone": pa.Column(float, _between(0, 1000), nullable=True),
        # Saharan dust storms can go far above 1000 µg/m³.
        "dust": pa.Column(float, _between(0, 20000), nullable=True),
        "european_aqi": pa.Column(float, _between(0, 1000), nullable=True),
    },
    unique=["city", "time"],
    strict=True,
    coerce=True,
)

WEATHER = pa.DataFrameSchema(
    {
        "city": pa.Column(str),
        "time": pa.Column("datetime64[ns]"),
        "temperature_2m": pa.Column(float, _between(-30, 60), nullable=True),
        "relative_humidity_2m": pa.Column(float, _between(0, 100), nullable=True),
        "precipitation": pa.Column(float, _between(0, 500), nullable=True),
        "wind_speed_10m": pa.Column(float, _between(0, 300), nullable=True),
        "wind_direction_10m": pa.Column(float, _between(0, 360), nullable=True),
    },
    unique=["city", "time"],
    strict=True,
    coerce=True,
)
