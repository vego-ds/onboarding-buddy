# System Architecture

## Current Architecture

Onboarding Buddy is a workflow operations MVP with Phase 3A assistant hardening and Phase 3B vector-RAG foundation.

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
  +--> Assistant Route
  |
  +--> Approved Knowledge Sources
  |
  +--> Knowledge Chunk Vector Index
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
```

## Implemented Components

- Streamlit frontend operations workspace
- FastAPI backend
- LangGraph workflow graph
- Supervisor Agent
- Intake Agent
- Task Planning Agent
- OpenRouter LLM client
- PostgreSQL support
- Render PostgreSQL support through `DATABASE_URL`
- Employee repository
- Task repository
- Approval repository
- Dependency repository
- Audit repository
- Workflow run repository
- Knowledge repository
- Assistant service
- Approved knowledge files

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

## Assistant Flow

1. A user asks a question from the Streamlit Assistant tab.
2. The frontend calls `POST /assistant/chat`.
3. The backend normalizes the stakeholder role.
4. The assistant retrieves approved knowledge chunks using deterministic local embeddings and cosine scoring.
5. If an employee ID is provided, existing employee, task, approval, and workflow run context is included.
6. Confidence score, citation metadata, and escalation state are calculated.
7. OpenRouter synthesizes a concise answer when confidence is sufficient.
8. If the LLM is unavailable or confidence is low, the assistant returns a deterministic source-grounded fallback or escalation answer.

The assistant is not part of the LangGraph workflow graph yet. It is a separate self-service API layer over approved knowledge and existing workflow records.

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
- knowledge chunks and embedding JSON for assistant retrieval

Approved assistant knowledge starts as markdown files under `knowledge/` and is indexed into `knowledge_chunks` with deterministic hashed embeddings.

PostgreSQL is the runtime database. Repository tests may use in-memory test doubles, but the application database adapter now requires a PostgreSQL `DATABASE_URL`.

## Operational Rules

- Tasks can be `Pending`, `In Progress`, `Completed`, `Blocked`, or `Failed`.
- Approval-required tasks cannot start until their approval is `Approved`.
- Downstream tasks cannot start until upstream dependencies are `Completed`.
- Premature start attempts mark the task `Blocked` and create a timeline event.
- Approval decisions and upstream completion can unlock blocked tasks back to `Pending`.
- Workflow run IDs, task IDs, approval IDs, and employee IDs are normalized at repository boundaries where needed.
- Assistant roles are normalized to Employee, Manager, HR, IT, or Security; unknown roles fall back to Employee.
- Assistant answers include citations, confidence labels, and escalation guidance when approved sources are weak.

## Deployment

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
- external embedding provider integration
- pgvector or managed vector database migration
- email or Slack notifications
- authentication and authorization
- RBAC enforcement
- calendar, chat, and HRMS integrations
- advanced audit dashboard
- Alembic migrations
- background workers
- multi-user roles
- production observability stack
