-- mart_city_daily must have one row per city and day, with at most 24 hours.
select city, day, count(*) as rows_for_day, max(hours) as hours
from {{ ref('mart_city_daily') }}
group by city, day
having count(*) > 1 or max(hours) > 24
