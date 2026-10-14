with source as (
    select * from {{ source('raw_edtech', 'enrollments') }}
)
select
    enrollment_id,
    student_id,
    course_id,
    cast(enrollment_date as timestamp) as enrolled_at,
    payment_method,
    status as enrollment_status,
    feedback
from source