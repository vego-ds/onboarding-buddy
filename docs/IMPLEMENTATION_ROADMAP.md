# Implementation Roadmap

## Current Status

Phase 1 is complete.

Phase 2 MVP scope is implemented and in stabilization:

- PostgreSQL support
- Render PostgreSQL deployment support
- task status management
- approval operations
- workflow run persistence
- agent run history
- workflow observability APIs
- task dependency enforcement
- locked/unlocked task state
- approval unlock logic
- timeline events
- frontend Operations workspace
- tests covering Phase 2 behavior

## Completed Phase 1

- project structure
- FastAPI backend
- Streamlit frontend
- SQLite persistence
- employee creation and listing
- onboarding plan generation
- Supervisor Agent
- Intake Agent
- Task Planning Agent
- LangGraph workflow
- OpenRouter integration
- deterministic fallback task generation
- initial tests and documentation

## Completed Phase 2 MVP

### Persistence and Deployment

- PostgreSQL support through `DATABASE_URL`
- SQLite fallback for local development and tests
- local PostgreSQL via Docker Compose
- Render PostgreSQL deployment support
- repeatable schema initialization with `schema.sql`

Alembic is not implemented yet.

### Workflow Operations

- approval queue
- approval decisions
- task status updates
- task dependency records
- dependency enforcement before `In Progress`
- approval unlock behavior
- blocked task state
- locked/unlocked task indicators
- workflow timeline events

### Observability

- workflow run records
- agent run records
- workflow run list API
- workflow run detail API
- employee timeline API
- Operations workspace workflow visibility

## Deployment Verification Checklist

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

## Recommended Next Phase

After Phase 2 MVP is deployed and verified, the next architecture milestones should be:

1. Alembic migrations
2. authentication and authorization
3. role-based approval routing
4. background workers for long-running workflows
5. notification infrastructure
6. production observability stack
7. Policy/Knowledge Agent and RAG only after workflow rules are stable

## Roadmap Only

These are not implemented yet:

- Policy/Knowledge Agent
- RAG/vector memory
- email or Slack notifications
- authentication and authorization
- advanced audit dashboard
- Alembic migrations
- background workers
- multi-user roles
- production observability stack
