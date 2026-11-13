-- Question 1: which city breathes worst? One row per city and complete past day.
-- WHO guideline for PM2.5: 15 µg/m³ as a 24-hour mean (2021).
select
    city,
    day,
    count(*) as hours,
    round(avg(pm2_5), 1) as pm25_avg,
    round(max(pm2_5), 1) as pm25_max,
    round(max(dust), 1) as dust_max,
    avg(pm2_5) > 15 as exceeds_who
from {{ ref('int_air_weather_hourly') }}
where period = 'past'
group by city, day
