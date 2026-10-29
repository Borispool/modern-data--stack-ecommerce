with source as (
    select * from {{ source('raw_edtech', 'courses') }}
)
select
    course_id,
    instructor_id,
    title as course_title,
    category,
    level as difficulty_level,
    case 
        when price < 0 then 0.00 
        else cast(price as numeric(10,2)) 
    end as price,
    is_active
from source