-- Question 3: which cities should be warned for tomorrow? Based on the forecast.
-- PM2.5: WHO 24-hour guideline (15 µg/m³). Dust: threshold chosen by the team (100 µg/m³).
select
    city,
    day,
    round(avg(pm2_5), 1) as pm25_avg_forecast,
    round(max(dust), 1) as dust_max_forecast,
    avg(pm2_5) > 15 as pm25_alert,
    max(dust) > 100 as dust_alert,
    avg(pm2_5) > 15 or max(dust) > 100 as alert
from {{ ref('int_air_weather_hourly') }}
where period = 'tomorrow'
group by city, day
