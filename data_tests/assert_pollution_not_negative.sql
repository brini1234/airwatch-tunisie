-- No pollution value can be negative. Returns the faulty rows (none = pass).
select city_hour_key, pm2_5, pm10, no2, ozone, dust
from {{ ref('stg_air_quality') }}
where pm2_5 < 0 or pm10 < 0 or no2 < 0 or ozone < 0 or dust < 0
