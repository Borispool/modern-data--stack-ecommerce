{{ config(materialized='table') }}

select
    e.enrollment_id,
    e.student_id,
    e.course_id,
    e.enrolled_at,
    e.payment_method,
    e.enrollment_status,
    c.price as amount_paid
from {{ ref('stg_enrollments') }} e
inner join {{ ref('dim_students') }} s on e.student_id = s.student_id
inner join {{ ref('stg_courses') }} c on e.course_id = c.course_id