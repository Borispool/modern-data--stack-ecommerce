with source as (
    select * from {{ source('raw_edtech', 'instructors') }}
)
select
    instructor_id,
    full_name as instructor_name,
    domain as expertise_domain,
    years_of_experience,
    rating
from source