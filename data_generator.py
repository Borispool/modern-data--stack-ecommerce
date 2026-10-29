import os
import random
from datetime import datetime, timedelta
import pandas as pd
from faker import Faker
from sqlalchemy import create_engine, text

fake = Faker('uk_UA')
Faker.seed(42)
random.seed(42)


DB_URL = "postgresql+psycopg2://admin:adminpassword@localhost:5432/edtech_dwh"
engine = create_engine(DB_URL)


def generate_instructors(num=20):
    print(f"Генерація {num} викладачів...")
    domains = ['Data Science', 'Web Development', 'Cybersecurity', 'Cloud Computing', 'UI/UX Design']
    instructors = []
    for i in range(1, num + 1):
        instructors.append({
            'instructor_id': i,
            'full_name': fake.name(),
            'domain': random.choice(domains),
            'years_of_experience': random.randint(2, 15),
            'rating': round(random.uniform(4.0, 5.0), 2)
        })
    return pd.DataFrame(instructors)

def generate_courses(num=40, instructor_ids=None):
    print(f"Генерація {num} курсів...")
    categories = ['Engineering', 'Design', 'Management', 'Marketing', 'Data Analytics']
    levels = ['Beginner', 'Intermediate', 'Advanced']
    courses = []
    for i in range(1, num + 1):
        courses.append({
            'course_id': i,
            'instructor_id': random.choice(instructor_ids),
            'title': f"{random.choice(categories)}: {fake.catch_phrase()}",
            'category': random.choice(categories),
            'level': random.choice(levels),
            'price': round(random.uniform(199.0, 4999.0), 2),
            'is_active': random.choice([True, True, True, False])
        })
    return pd.DataFrame(courses)

def generate_students(num=500):
    print(f"Генерація {num} студентів (з брудними даними)...")
    students = []
    for i in range(1, num + 1):
        email = fake.email() if random.random() > 0.1 else None
        students.append({
            'student_id': i,
            'full_name': fake.name(),
            'email': email,
            'city': fake.city(),
            'registration_date': fake.date_between(start_date='-2y', end_date='today')
        })
    df = pd.DataFrame(students)
    duplicates = df.sample(frac=0.05, random_state=42)
    df = pd.concat([df, duplicates], ignore_index=True)
    return df



def generate_enrollments(num=1200, student_ids=None, course_ids=None):
    print(f"Генерація {num} записів на курси (enrollments)...")
    enrollments = []
    payment_methods = ['Card', 'Apple Pay', 'Google Pay', 'Bank Transfer']
    statuses = ['completed', 'pending', 'refunded']

    for i in range(1, num + 1):
        enrollment_date = fake.date_time_between(start_date='-1y', end_date='now')
        feedback = fake.sentence(nb_words=8) if random.random() > 0.2 else None
        
        enrollments.append({
            'enrollment_id': i,
            'student_id': random.choice(student_ids),
            'course_id': random.choice(course_ids),
            'enrollment_date': enrollment_date,
            'payment_method': random.choice(payment_methods),
            'status': random.choices(statuses, weights=[85, 10, 5])[0],
            'feedback': feedback
        })
    return pd.DataFrame(enrollments)

def generate_lesson_completions(num=4000, student_ids=None, course_ids=None):
    print(f"Генерація {num} завершень уроків (lesson_completions)...")
    completions = []
    for i in range(1, num + 1):
        completion_time = fake.date_time_between(start_date='-6m', end_date='now')
        completions.append({
            'completion_id': i,
            'student_id': random.choice(student_ids),
            'course_id': random.choice(course_ids),
            'lesson_number': random.randint(1, 20),
            'score': random.randint(50, 100),
            'completed_at': completion_time
        })
    return pd.DataFrame(completions)


def generate_reviews(num=800, student_ids=None, course_ids=None):
    print(f"Генерація {num} відгуків на курси (reviews)...")
    reviews = []
    for i in range(1, num + 1):
        comment = fake.sentence(nb_words=10) if random.random() > 0.2 else None
        reviews.append({
            'review_id': i,
            'student_id': random.choice(student_ids),
            'course_id': random.choice(course_ids),
            'rating': random.randint(1, 5),
            'comment': comment,
            'review_date': fake.date_time_between(start_date='-1y', end_date='now')
        })
    return pd.DataFrame(reviews)

def load_data_to_dwh():
    print("\n--- СТАРТ ГЕНЕРАЦІЇ ДАНИХ ---")
    df_instructors = generate_instructors(num=20)
    df_courses = generate_courses(num=40, instructor_ids=df_instructors['instructor_id'].tolist())
    df_students = generate_students(num=500)

    unique_student_ids = df_students['student_id'].dropna().unique().tolist()
    course_ids = df_courses['course_id'].tolist()

    df_enrollments = generate_enrollments(num=1200, student_ids=unique_student_ids, course_ids=course_ids)
    df_completions = generate_lesson_completions(num=4000, student_ids=unique_student_ids, course_ids=course_ids)
    df_reviews = generate_reviews(num=800, student_ids=unique_student_ids, course_ids=course_ids)

    print("\n--- ЗБЕРЕЖЕННЯ В DATA LAKE (PARQUET) ---")
    os.makedirs('data_lake', exist_ok=True)
    
    df_instructors.to_parquet('data_lake/raw_instructors.parquet', index=False)
    df_courses.to_parquet('data_lake/raw_courses.parquet', index=False)
    df_students.to_parquet('data_lake/raw_students.parquet', index=False)
    df_enrollments.to_parquet('data_lake/raw_enrollments.parquet', index=False)
    df_completions.to_parquet('data_lake/raw_lesson_completions.parquet', index=False)
    df_reviews.to_parquet('data_lake/raw_reviews.parquet', index=False)
    
    print("Файли успішно збережено у папці /data_lake")

    print("\n--- ЗАВАНТАЖЕННЯ ДАНИХ У POSTGRESQL (СХЕМА: raw) ---")
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw;"))
        for tbl in ['instructors', 'courses', 'students', 'enrollments', 'lesson_completions', 'reviews']:
            conn.execute(text(f"DROP VIEW IF EXISTS analytics.stg_{tbl} CASCADE;"))
            conn.execute(text(f"DROP TABLE IF EXISTS raw.{tbl} CASCADE;"))
        conn.commit()

    df_instructors.to_sql('instructors', engine, schema='raw', if_exists='append', index=False)
    print("Таблиця raw.instructors завантажена.")

    df_courses.to_sql('courses', engine, schema='raw', if_exists='append', index=False)
    print("Таблиця raw.courses завантажена.")

    df_students.to_sql('students', engine, schema='raw', if_exists='append', index=False)
    print("Таблиця raw.students завантажена.")

    df_enrollments.to_sql('enrollments', engine, schema='raw', if_exists='append', index=False)
    print("Таблиця raw.enrollments завантажена.")

    df_completions.to_sql('lesson_completions', engine, schema='raw', if_exists='append', index=False)
    print("Таблиця raw.lesson_completions завантажена.")

    df_reviews.to_sql('reviews', engine, schema='raw', if_exists='append', index=False)
    print("Таблиця raw.reviews завантажена.")       

    print("\n[SUCCESS] Усі таблиці успішно згенеровані та завантажені у схему 'raw'!")

if __name__ == "__main__":
    load_data_to_dwh()