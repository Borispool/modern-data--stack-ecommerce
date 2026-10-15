from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import sys

# Додаємо шлях до папки зі скриптами
SCRIPTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'scripts'))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from data_generator import load_data_to_dwh

# Шляхи до dbt проєкту
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
DBT_PROJECT_DIR = os.path.join(PROJECT_ROOT, 'edtech_dbt')
DBT_PROFILES_DIR = os.path.join(PROJECT_ROOT, 'edtech_dbt')

default_args = {
    'owner': 'edtech_engineer',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'edtech_elt_pipeline',
    default_args=default_args,
    description='End-to-End ELT Pipeline для освітньої платформи EdTech',
    schedule='@daily',
    catchup=False
) as dag:

    # Task 1: Генерація та завантаження в raw шар
    extract_load_task = PythonOperator(
        task_id='extract_and_load_raw_data',
        python_callable=load_data_to_dwh
    )

    # Task 2: Трансформація даних (dbt run)
    dbt_run_task = BashOperator(
        task_id='dbt_run_transformations',
        bash_command=f'dbt run --project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROFILES_DIR}'
    )

    # Task 3: Перевірка якості даних (dbt test)
    dbt_test_task = BashOperator(
        task_id='dbt_test_quality_gates',
        bash_command=f'dbt test --select dim_students fct_enrollments --project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROFILES_DIR}'
    )

    # Налаштування залежностей (Data Pipeline Graph)
    extract_load_task >> dbt_run_task >> dbt_test_task