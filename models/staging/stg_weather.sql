select
    city,
    time as hour_at,
    city || ' ' || strftime(time, '%Y-%m-%d %H:00') as city_hour_key,
    temperature_2m as temperature,
    relative_humidity_2m as humidity,
    precipitation,
    wind_speed_10m as wind_speed,
    wind_direction_10m as wind_direction,
    _loaded_at
from {{ source('raw', 'weather') }}
