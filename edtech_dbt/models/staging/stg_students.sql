with source as (
    select * from {{ source('raw_edtech', 'students') }}
),
deduplicated as (
    select
        student_id,
        full_name,
        coalesce(email, 'unknown@edtech.com') as email,
        city,
        cast(registration_date as date) as registration_date,
        row_number() over (partition by student_id order by registration_date desc) as rn
    from source
)
select
    student_id,
    full_name,
    email,
    city,
    registration_date
from deduplicated
where rn = 1