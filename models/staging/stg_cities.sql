select
    city,
    latitude,
    longitude
from {{ source('raw', 'cities') }}
