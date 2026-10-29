{{ config(materialized='table') }}

select
    c.course_id,
    c.course_title,
    c.category,
    c.difficulty_level,
    c.price,
    c.is_active,
    i.instructor_name,
    i.expertise_domain
from {{ ref('stg_courses') }} c
left join {{ ref('stg_instructors') }} i on c.instructor_id = i.instructor_id