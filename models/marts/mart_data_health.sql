-- Data health, one row per city: is the data fresh and complete?
with yesterday as (
    select max(day) as day
    from {{ ref('stg_air_quality') }}
    where period = 'past'
)

select
    cities.city,
    max(air._loaded_at) as last_loaded_at,
    count(air.city_hour_key) filter (where air.day = yesterday.day) as hours_yesterday,
    count(air.city_hour_key) filter (where air.day = yesterday.day) = 24 as complete_yesterday,
    count(air.city_hour_key) filter (where air.pm2_5 is null) as missing_pm25
from {{ ref('stg_cities') }} as cities
cross join yesterday
left join {{ ref('stg_air_quality') }} as air
    on cities.city = air.city
group by cities.city
