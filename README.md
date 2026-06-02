# Onboarding Buddy

Onboarding Buddy is an AI workflow product for employee onboarding. It combines a Streamlit dashboard, FastAPI backend, PostgreSQL-ready persistence, and a LangGraph supervisor workflow to create employee records, generate onboarding task plans, review HR approvals, and update task status from a usable HR operations interface.

The project is intentionally scoped as a controlled onboarding workflow, not an unrestricted autonomous agent.

## Current Scope

- Create employee onboarding records
- List recent employees in a dashboard
- Generate onboarding plans through a supervisor-controlled LangGraph flow
- Validate employee profile data with an Intake Agent
- Generate structured onboarding tasks with a Task Planning Agent
- Fall back to deterministic default tasks when LLM generation fails
- View generated tasks, owners, priorities, approval flags, and task metrics
- Create approval records for approval-required tasks
- Review approval requests and record HR decisions
- Update onboarding task status
- Enforce task dependencies before downstream work can start
- Persist audit events for approvals, task changes, employee edits, and workflow requests
- View employee workflow history from the operations workspace
- Persist workflow runs and agent execution summaries for observability
- Track employee onboarding lifecycle status such as `PENDING`, `PLAN_READY`, and `FAILED`

## Tech Stack

- Frontend: Streamlit
- Backend: FastAPI
- Workflow orchestration: LangGraph
- LLM provider: OpenRouter
- Database: PostgreSQL for Phase 2 infrastructure, with SQLite as a local fallback
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
PostgreSQL / SQLite Database
```

The Supervisor Agent owns routing decisions. Specialist agents only perform focused tasks and communicate through structured workflow state.

## Workflow

```text
Create Employee
  |
  v
Supervisor routes to Intake Agent
  |
  v
Intake validates employee profile
  |
  v
Supervisor routes to Task Planning Agent
  |
  v
Task Planning Agent generates or falls back to 6 onboarding tasks
  |
  v
Tasks are saved to the configured relational database
  |
  v
Employee status updates to PLAN_READY
```

## Implemented API Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Backend health check |
| `POST` | `/employees` | Create employee onboarding record |
| `GET` | `/employees` | List recent employee records |
| `GET` | `/employees/{employee_id}` | Get one employee |
| `PUT` | `/employees/{employee_id}` | Edit employee onboarding details |
| `POST` | `/employees/{employee_id}/generate-onboarding-plan` | Run onboarding workflow |
| `GET` | `/employees/{employee_id}/tasks` | Get generated onboarding tasks |
| `GET` | `/approvals` | List approval requests |
| `PATCH` | `/approvals/{approval_id}` | Record an approval decision |
| `GET` | `/tasks/{task_id}` | Get one onboarding task |
| `GET` | `/tasks/{task_id}/dependencies` | Get upstream task dependencies |
| `PATCH` | `/tasks/{task_id}/status` | Update task status |
| `GET` | `/employees/{employee_id}/timeline` | Get employee workflow history |
| `GET` | `/workflow-runs` | List workflow executions |
| `GET` | `/workflow-runs/{workflow_run_id}` | Get workflow and agent execution details |

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create `.env`:

```text
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=meta-llama/llama-3.1-8b-instruct
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
DATABASE_URL=postgresql://onboarding_buddy:onboarding_buddy@localhost:5432/onboarding_buddy
```

Start PostgreSQL for local Phase 2 development:

```bash
docker compose up -d postgres
```

Initialize the database schema:

```bash
python -m database.db
```

For lightweight local demos, set `DATABASE_URL=sqlite:///onboarding_buddy.db` before initializing the database.

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

## Test

```bash
python -m compileall frontend backend database agents schemas tests
python -m pytest
```

## Demo Flow

1. Start FastAPI and Streamlit.
2. Create a new employee record.
3. Confirm the employee appears in the dashboard and directory.
4. Generate the onboarding plan.
5. Review the task metrics and generated task cards.
6. Open workflow details to show supervisor routing and agent outputs.
7. Fetch tasks again from the Tasks tab to show persistence.

## Portfolio Highlights

- Product-style frontend rather than a raw API demo
- Supervisor-based multi-agent workflow with LangGraph
- Deterministic fallback behavior for reliability
- Structured task validation before database persistence
- Duplicate task prevention
- Clear API separation between frontend, backend, workflow, and database layers
- PostgreSQL-ready persistence boundary with SQLite fallback for local demos
- Approval workflow and task status operations for Phase 2
- Dependency enforcement and audit timeline for workflow realism
- Workflow-run persistence for execution observability

## Roadmap

These are intentionally deferred beyond Phase 1:

- Policy and Knowledge Agent
- Welcome email draft review
- Calendar and manager follow-up agents
- Authentication and role-based access
- Deployment to a hosted environment

## Repository Structure

```text
agents/               LangGraph agent logic and workflow state
backend/              FastAPI app and routes
database/             relational schema, connection adapter, and repositories
docs/                 Architecture, API, workflow, and portfolio documentation
frontend/             Streamlit dashboard
llm/                  OpenRouter client
schemas/              Pydantic request/response models
scripts/              Local workflow utilities
tests/                Agent and workflow safety tests
docker-compose.yml    Local PostgreSQL service for Phase 2 development
```
