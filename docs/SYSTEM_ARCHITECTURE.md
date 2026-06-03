# System Architecture

## Current Architecture

Onboarding Buddy is a Phase 2 workflow operations MVP.

```text
Streamlit Frontend
  |
  v
FastAPI Backend
  |
  +--> Employee Routes
  +--> Task Routes
  +--> Approval Routes
  +--> Workflow Run Routes
  |
  v
LangGraph Workflow Service
  |
  v
Supervisor Agent
  |
  +--> Intake Agent
  |
  +--> Task Planning Agent
  |
  v
Repository Layer
  |
  v
PostgreSQL through DATABASE_URL
  or
SQLite fallback
```

## Implemented Components

- Streamlit frontend operations workspace
- FastAPI backend
- LangGraph workflow graph
- Supervisor Agent
- Intake Agent
- Task Planning Agent
- OpenRouter LLM client
- SQLite fallback
- PostgreSQL support
- Render PostgreSQL support through `DATABASE_URL`
- Employee repository
- Task repository
- Approval repository
- Dependency repository
- Audit repository
- Workflow run repository

## Workflow Execution

1. HR creates or selects an employee in the frontend.
2. The frontend calls `POST /employees/{employee_id}/generate-onboarding-plan`.
3. The backend creates a durable workflow run.
4. LangGraph starts at the Supervisor Agent.
5. Supervisor routes to Intake Agent.
6. Intake validates employee data.
7. Supervisor routes to Task Planning Agent.
8. Task Planning generates or falls back to six validated onboarding tasks.
9. Tasks, approvals, dependencies, audit events, workflow runs, and agent runs are persisted.
10. Employee status becomes `PLAN_READY` when tasks exist.

## Persistence

The database stores:

- employees
- onboarding tasks
- task dependencies
- approvals
- audit logs
- workflow runs
- agent runs
- workflow state table reserved for future state snapshots

PostgreSQL is the Phase 2 production-oriented database. SQLite remains supported for local fallback and tests.

## Operational Rules

- Tasks can be `Pending`, `In Progress`, `Completed`, `Blocked`, or `Failed`.
- Approval-required tasks cannot start until their approval is `Approved`.
- Downstream tasks cannot start until upstream dependencies are `Completed`.
- Premature start attempts mark the task `Blocked` and create a timeline event.
- Approval decisions and upstream completion can unlock blocked tasks back to `Pending`.
- Workflow run IDs, task IDs, approval IDs, and employee IDs are normalized at repository boundaries where needed.

## Deployment

Local SQLite:

```bash
DATABASE_URL=sqlite:///onboarding_buddy.db
python -m database.db
```

Local PostgreSQL:

```bash
docker compose up -d
DATABASE_URL=postgresql://onboarding_buddy:onboarding_buddy@localhost:5432/onboarding_buddy
python -m database.db
```

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

Streamlit Cloud secret:

```toml
API_BASE_URL = "https://onboarding-buddy-api.onrender.com"
```

## Roadmap Only

The following are not implemented yet:

- Policy/Knowledge Agent
- RAG/vector memory
- email or Slack notifications
- authentication and authorization
- advanced audit dashboard
- Alembic migrations
- background workers
- multi-user roles
- production observability stack
