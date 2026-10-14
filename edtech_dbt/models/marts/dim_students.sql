{{ config(materialized='table') }}

select
    student_id,
    full_name,
    email,
    city,
    registration_date
from {{ ref('stg_students') }}