{{ config(materialized='table') }}

select
    lc.completion_id,
    lc.student_id,
    lc.course_id,
    lc.lesson_number,
    lc.score,
    lc.completed_at
from {{ ref('stg_lesson_completions') }} lc
inner join {{ ref('dim_students') }} s on lc.student_id = s.student_id