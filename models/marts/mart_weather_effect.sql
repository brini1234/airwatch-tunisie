-- Question 2: do wind and rain lower pollution? Average PM2.5 by wind strength and rain.
select
    case
        when wind_speed < 10 then '1 - calm (< 10 km/h)'
        when wind_speed < 25 then '2 - moderate (10-25 km/h)'
        else '3 - strong (> 25 km/h)'
    end as wind_class,
    precipitation > 0 as rainy,
    count(*) as hours,
    round(avg(pm2_5), 1) as pm25_avg
from {{ ref('int_air_weather_hourly') }}
where period != 'tomorrow'
    and pm2_5 is not null
    and wind_speed is not null
    and precipitation is not null
group by wind_class, rainy
