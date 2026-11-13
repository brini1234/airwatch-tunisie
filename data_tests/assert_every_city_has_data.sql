-- Every city of data/cities.csv must have air quality data.
select city
from {{ ref('mart_data_health') }}
where last_loaded_at is null
