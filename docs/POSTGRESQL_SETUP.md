# PostgreSQL Setup

## Goal

Phase 2 uses PostgreSQL as the production-oriented persistence layer for workflow orchestration data.

The app still supports SQLite for lightweight local demos and tests, but PostgreSQL should be used when validating operational workflow behavior.

## Start PostgreSQL Locally

```bash
docker compose up -d postgres
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

For SQLite fallback:

```text
DATABASE_URL=sqlite:///onboarding_buddy.db
```

## Initialize Schema

```bash
python -m database.db
```

The same schema file is used for SQLite and PostgreSQL.

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

## Notes

The current implementation uses a small database adapter rather than SQLAlchemy/Alembic. That keeps the migration scoped while preserving the existing repository boundary.

Alembic should be introduced before the schema starts changing frequently across deployed environments.
