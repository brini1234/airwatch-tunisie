-- One row per city and hour. The API always sends 2 past days and 2 forecast days,
-- so the last day in the data is "tomorrow" and the day before it is "today".
with source as (
    select * from {{ source('raw', 'air_quality') }}
),

reference as (
    select max(cast(time as date)) - interval 1 day as today
    from source
)

select
    source.city,
    source.time as hour_at,
    cast(source.time as date) as day,
    extract(hour from source.time) as hour,
    source.city || ' ' || strftime(source.time, '%Y-%m-%d %H:00') as city_hour_key,
    source.pm2_5,
    source.pm10,
    source.nitrogen_dioxide as no2,
    source.ozone,
    source.dust,
    source.european_aqi,
    case
        when cast(source.time as date) < reference.today then 'past'
        when cast(source.time as date) = reference.today then 'today'
        else 'tomorrow'
    end as period,
    source._loaded_at
from source
cross join reference
