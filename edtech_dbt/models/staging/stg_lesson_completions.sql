with source as (
    select * from {{ source('raw_edtech', 'lesson_completions') }}
)
select
    completion_id,
    student_id,
    course_id,
    lesson_number,
    score,
    cast(completed_at as timestamp) as completed_at
from source