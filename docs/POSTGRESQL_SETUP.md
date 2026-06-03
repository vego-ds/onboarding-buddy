# PostgreSQL Setup

## Goal

Phase 2 uses PostgreSQL as the production-oriented persistence layer for workflow orchestration data.

PostgreSQL is the supported runtime database for Phase 2.

## Start PostgreSQL Locally

```bash
docker compose up -d
```

The local container creates:

```text
database: onboarding_buddy
user: onboarding_buddy
password: onboarding_buddy
port: 5432
```

## Configure Environment

Use this value in `.env`:

```text
DATABASE_URL=postgresql://onboarding_buddy:onboarding_buddy@localhost:5432/onboarding_buddy
```

## Initialize Schema

```bash
python -m database.db
```

The schema file is used to initialize PostgreSQL tables and indexes.

## Verify

```bash
python -m compileall frontend backend database agents schemas tests
python -m pytest
uvicorn backend.main:app --reload
streamlit run frontend/app.py
```

Then test the core workflow:

```text
POST /employees
POST /employees/{employee_id}/generate-onboarding-plan
GET /workflow-runs
GET /workflow-runs/{workflow_run_id}
GET /employees/{employee_id}/tasks
GET /employees/{employee_id}/timeline
```

## Render Backend Deployment

Use a Render PostgreSQL database and set `DATABASE_URL` to the Render Internal Database URL.

Render backend Start Command:

```bash
python -m database.db && uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

Render environment variables:

```text
DATABASE_URL=<Render Internal Database URL>
OPENROUTER_API_KEY=<secret>
OPENROUTER_MODEL=openrouter/free
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
LANGSMITH_TRACING=false
APP_ENV=production
```

## Streamlit Cloud

Set this secret:

```toml
API_BASE_URL = "https://onboarding-buddy-api.onrender.com"
```

## Notes

The current implementation uses a small database adapter rather than SQLAlchemy/Alembic. That keeps the migration scoped while preserving the existing repository boundary.

Alembic is not implemented yet. The current `schema.sql` is safe to run repeatedly for creating missing tables and indexes, but it does not migrate existing table definitions. Alembic or dedicated migration scripts should be introduced before making repeated deployed schema changes.
