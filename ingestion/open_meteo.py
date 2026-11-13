"""Extract: call the two Open-Meteo APIs and turn their answer into a table."""

import time

import pandas as pd
import requests

AIR_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

AIR_VARIABLES = ["pm2_5", "pm10", "nitrogen_dioxide", "ozone", "dust", "european_aqi"]
WEATHER_VARIABLES = [
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "wind_speed_10m",
    "wind_direction_10m",
]

PAST_DAYS = 2
FORECAST_DAYS = 2
TIMEZONE = "Africa/Tunis"


def fetch(url, latitude, longitude, variables, retries=3, wait_seconds=5):
    """Call one API for one place. Try again a few times if the network fails."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ",".join(variables),
        "past_days": PAST_DAYS,
        "forecast_days": FORECAST_DAYS,
        "timezone": TIMEZONE,
    }
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            if attempt == retries:
                raise
            time.sleep(wait_seconds)


def to_frame(payload, city, variables):
    """One row per hour: city, time, then one column per variable."""
    hourly = payload["hourly"]
    frame = pd.DataFrame({"time": pd.to_datetime(hourly["time"])})
    for variable in variables:
        frame[variable] = pd.to_numeric(pd.Series(hourly[variable]), errors="coerce")
    frame.insert(0, "city", city)
    return frame
