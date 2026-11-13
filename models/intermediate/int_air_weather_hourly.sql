-- Pollution and weather side by side, hour by hour.
select
    air.city_hour_key,
    air.city,
    air.hour_at,
    air.day,
    air.hour,
    air.period,
    air.pm2_5,
    air.pm10,
    air.no2,
    air.ozone,
    air.dust,
    air.european_aqi,
    weather.temperature,
    weather.humidity,
    weather.precipitation,
    weather.wind_speed
from {{ ref('stg_air_quality') }} as air
left join {{ ref('stg_weather') }} as weather
    on air.city_hour_key = weather.city_hour_key
