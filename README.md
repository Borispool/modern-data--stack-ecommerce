# modern-data--stack-ecommerce
# EdTech Data Platform: End-to-End ELT Analytics Pipeline

A robust, modern data platform built to ingest, model, orchestrate, and visualize learning analytics for an online educational platform. The pipeline processes student behaviors, course catalog interactions, enrollment funnels, and granular lesson completion events.

## Architecture Overview

The system follows the **ELT (Extract, Load, Transform)** paradigm and **Kimball Dimensional Modeling (Star Schema)** to separate operational load from analytical querying:

[ Mock OLTP System (Python Faker) ]
│
▼ (Extract & Load)
[ PostgreSQL: Raw Storage Layer (raw schema) ]
│
▼ (Transform via dbt Core)
[ PostgreSQL: Analytics Marts (analytics schema) ]
├── dim_students
├── dim_courses
├── dim_instructors
├── fct_enrollments
└── fct_lesson_completions
│
┌────────┴────────┐
▼                 ▼
[ Apache Airflow ]   [ Metabase BI ]
(Orchestration)     (Dashboards)


### Core Components
- **Data Ingestion (E & L):** Python scripts simulate upstream transactional data feeds, handle API-level pagination/generation, and load unmodified data into raw landing tables (`raw.students`, `raw.courses`, `raw.instructors`, `raw.enrollments`, `raw.lesson_completions`).
- **Data Transformation (T):** `dbt Core` builds modular, tested SQL pipelines with explicit staging (`stg_`) layers for deduplication, schema casting, and null handling, outputting to analytics-ready dimension and fact marts.
- **Workflow Orchestration:** `Apache Airflow` coordinates dependent tasks (Ingestion ➔ dbt Run ➔ dbt Test) on a deterministic schedule with automatic retries and SLA monitoring.
- **Business Intelligence & Lineage:** `Metabase` delivers executive dashboards tracking retention, drop-off rates, and instructor performance. `dbt docs` provides DAG lineage and automated data dictionary tracking.

---

## Data Model (Star Schema)

### Dimensions (`analytics` schema)
- **`dim_students`**: Unique student attributes, contact validity flags, cohort registration dates, and regional metadata.
- **`dim_courses`**: Course catalog detailing category hierarchy, difficulty tiers, pricing, and active publication status.
- **`dim_instructors`**: Verified educator profiles, expertise domains, and operational status.

### Facts (`analytics` schema)
- **`fct_enrollments`**: Course purchase and enrollment events, payment tracking, and student acquisition source.
- **`fct_lesson_completions`**: Granular progress logs capturing lesson duration, quiz attempts, completion timestamps, and engagement state.

---

## Repository Structure

├── airflow/                 
│   └── dags/
│       └── edtech_pipeline.py
├── dbt_transforms/          
│   ├── models/
│   │   ├── staging/          
│   │   └── marts/            
│   ├── tests/                
│   └── dbt_project.yml
├── scripts/                  
│   └── data_generator.py
├── docker-compose.yml        
├── requirements.txt          
└── README.md


---

## Quickstart & Deployment

### Prerequisites
- Docker Engine & Docker Compose (v2.20+)
- Python 3.9+

### 1. Infrastructure Setup
Spin up the analytical storage engine and BI container:
```bash
docker compose up -d
Verify services are healthy:

Bash
docker compose ps
2. Environment Configuration
Set up the Python execution environment:

Bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
3. Pipeline Execution
Run the synthetic data ingestion engine:

Bash
python scripts/data_generator.py
Execute dbt models and quality test suites:

Bash
cd dbt_transforms
dbt deps
dbt run
dbt test

4. Orchestration & Dashboards
Airflow Web UI: http://localhost:8080 (Manage, inspect, and trigger DAGs)

Metabase BI: http://localhost:3000 (Access analytical reports and KPIs)

dbt Documentation & Lineage: http://localhost:8081 (Run via dbt docs serve)

Data Quality & Governance
Uniqueness & Referential Integrity: Primary keys and foreign keys across fact and dimension tables are validated on every pipeline run using dbt schema assertions.

Handling Incomplete Records: Upstream missing values (e.g., student contact info or optional feedback) are caught in the staging layer and normalized using surrogate fallback keys and deterministic Coalesce logic.

Idempotency: All ingestion jobs support safe re-runs via explicit truncations or upsert patterns without producing duplicate analytical events.