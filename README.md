# Onboarding Buddy

Onboarding Buddy is an AI-assisted employee onboarding workflow platform. It combines a Streamlit operations workspace, FastAPI backend, LangGraph supervisor workflow, OpenRouter LLM integration, approved-source onboarding assistant, and relational persistence to create employee records, generate onboarding plans, manage approvals, enforce task dependencies, and inspect workflow execution history.

The project is intentionally scoped as a controlled workflow orchestration prototype, not an unrestricted autonomous agent.

## Implemented Now

- Supervisor Agent
- Intake Agent
- Task Planning Agent
- LangGraph workflow
- OpenRouter LLM integration with deterministic fallback tasks
- FastAPI backend
- Streamlit frontend
- PostgreSQL support through `DATABASE_URL`
- Render PostgreSQL deployment support
- Employee create, list, detail, and edit
- Onboarding plan generation
- Task lifecycle management
- Approval operations
- Workflow run persistence
- Agent run history
- Workflow observability APIs
- Task dependency enforcement
- Locked/unlocked task state
- Approval unlock logic
- Timeline events
- Frontend Operations workspace
- Phase 3 onboarding assistant foundation using approved local knowledge sources
- Role-aware assistant responses for Employee, Manager, HR, IT, and Security contexts
- Optional employee workflow context in assistant responses
- Answer guardrails for insufficient approved knowledge
- Source citations, confidence scoring, and escalation messages
- Approved knowledge chunking and deterministic hashed embeddings
- PostgreSQL-backed `knowledge_chunks` vector index
- Assistant knowledge reindex endpoint
- Defense-in-depth assistant guardrails
- Input safety classification before retrieval or LLM synthesis
- XML isolation for untrusted RAG/tool context
- Final response inspection for PII and prompt exfiltration
- Phase 4 authentication foundation
- User registration, login, and `/auth/me`
- JWT bearer tokens
- Password hashing with PBKDF2
- RBAC roles: `employee`, `manager`, `hr_admin`, `admin`
- Protected employee, task, approval, workflow, assistant, and knowledge-index APIs
- Assistant role derived from authenticated user identity
- Tests covering Phase 2 behavior and Phase 3 assistant/RAG behavior

## Roadmap Only

- Policy/Knowledge Agent
- External embedding provider integration
- pgvector or managed vector database upgrade
- RAG evaluation benchmark suite
- Email or Slack notifications
- Calendar, chat, and HRMS integrations
- Advanced audit dashboard
- Alembic migrations
- Background workers
- Multi-user roles
- Production observability stack

## Tech Stack

- Frontend: Streamlit
- Backend: FastAPI
- Workflow orchestration: LangGraph
- LLM provider: OpenRouter
- Database: PostgreSQL
- Validation: Pydantic
- Tests: pytest

## Architecture

```text
HR User
  |
  v
Streamlit Frontend
  |
  v
FastAPI Backend
  |
  +--> Employee / Task / Approval / Workflow APIs
  |
  +--> Assistant API
       |
       +--> Approved Knowledge Sources
  |
  v
LangGraph Workflow
  |
  v
Supervisor Agent
  |
  +--> Intake Agent
  |
  +--> Task Planning Agent
  |
  v
PostgreSQL
```

The frontend never calls agents directly. It calls FastAPI endpoints, and the backend controls workflow execution, persistence, and operational state.

## Implemented API Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Backend health check |
| `POST` | `/auth/register` | Create a user and return JWT |
| `POST` | `/auth/login` | Authenticate user and return JWT |
| `GET` | `/auth/me` | Return authenticated user |
| `GET` | `/employees` | List employee records |
| `POST` | `/employees` | Create employee onboarding record |
| `GET` | `/employees/{employee_id}` | Get one employee |
| `PUT` | `/employees/{employee_id}` | Edit employee onboarding details |
| `GET` | `/employees/{employee_id}/tasks` | Get employee tasks and summary metrics |
| `GET` | `/employees/{employee_id}/timeline` | Get employee workflow timeline |
| `POST` | `/employees/{employee_id}/generate-onboarding-plan` | Run onboarding workflow |
| `GET` | `/tasks/{task_id}` | Get task detail and enforcement state |
| `GET` | `/tasks/{task_id}/dependencies` | Get upstream dependencies and locked/unlocked state |
| `PATCH` | `/tasks/{task_id}/status` | Update task lifecycle status |
| `GET` | `/approvals` | List approval requests |
| `GET` | `/approvals/{approval_id}` | Get one approval |
| `PATCH` | `/approvals/{approval_id}` | Record approval decision |
| `GET` | `/workflow-runs` | List workflow executions |
| `GET` | `/workflow-runs/{workflow_run_id}` | Get workflow and agent execution details |
| `POST` | `/assistant/chat` | Ask the approved-source onboarding assistant |
| `POST` | `/assistant/knowledge/reindex` | Rebuild the approved knowledge vector index |

## Local Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Local PostgreSQL

Start PostgreSQL:

```bash
docker compose up -d
```

Set the database URL:

```bash
export DATABASE_URL=postgresql://onboarding_buddy:onboarding_buddy@localhost:5432/onboarding_buddy
python -m database.db
```

## Run Locally

Start the backend:

```bash
uvicorn backend.main:app --reload
```

Start the frontend:

```bash
streamlit run frontend/app.py
```

Open:

```text
http://127.0.0.1:8501
```

## Render Backend Deployment

Use a Render PostgreSQL database and set the backend environment variables:

```text
DATABASE_URL=<Render Internal Database URL>
OPENROUTER_API_KEY=<secret>
OPENROUTER_MODEL=openrouter/free
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
LANGSMITH_TRACING=false
APP_ENV=production
```

Render backend Start Command:

```bash
python -m database.db && uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

## Streamlit Cloud Deployment

Set this Streamlit secret:

```toml
API_BASE_URL = "https://onboarding-buddy-api.onrender.com"
```

For local development, the frontend falls back to:

```text
http://127.0.0.1:8000
```

## Test

```bash
./venv/bin/python -m compileall frontend backend database agents schemas tests
./venv/bin/python -m pytest
```

## Assistant And RAG Scope

Phase 3A strengthened the assistant with answer guardrails, citations, confidence scoring, escalation behavior, and tests. Phase 3B adds a vector-RAG foundation using approved local knowledge chunks, deterministic hashed embeddings, PostgreSQL-backed `knowledge_chunks`, and cosine retrieval.

It is not yet an enterprise SSO system, Slack/email/calendar integration, HRMS integration, external embedding pipeline, or managed vector database deployment.

## Authentication And RBAC

Phase 4 adds a real user identity layer. Protected API calls require a Bearer token from `/auth/login` or `/auth/register`.

Roles:

```text
employee
manager
hr_admin
admin
```

Access model:

- employees can access their linked employee onboarding record
- managers can access direct reports linked through `manager_id`
- HR admins and admins can access all onboarding records and workflow operations
- only HR admins and admins can reindex assistant knowledge
- the assistant uses the authenticated user's role from the JWT-backed user record, not request-body role text

Production note: replace the development `JWT_SECRET` with a long random secret in every deployed environment.

## Migration Note

The current implementation uses a small database adapter and a repeatable `schema.sql` file against PostgreSQL. Alembic is not implemented yet. If schema changes become frequent across deployed environments, add Alembic or dedicated migration scripts before making destructive table changes.

## Repository Structure

```text
agents/               LangGraph agent logic and workflow state
backend/              FastAPI app and routes
database/             relational schema, connection adapter, and repositories
docs/                 Architecture, API, workflow, and portfolio documentation
frontend/             Streamlit dashboard
knowledge/            Approved onboarding knowledge for assistant answers
llm/                  OpenRouter client
schemas/              Pydantic request models
scripts/              Local workflow utilities
tests/                Agent, repository, route, and database tests
docker-compose.yml    Local PostgreSQL service for Phase 2 development
```
