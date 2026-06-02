# Onboarding Buddy

Onboarding Buddy is a Phase 1 AI workflow product for employee onboarding. It combines a Streamlit dashboard, FastAPI backend, SQLite persistence, and a LangGraph supervisor workflow to create employee records, generate onboarding task plans, and review task status from a usable HR operations interface.

The project is intentionally scoped as a controlled onboarding workflow, not an unrestricted autonomous agent.

## Current Phase 1 Scope

- Create employee onboarding records
- List recent employees in a dashboard
- Generate onboarding plans through a supervisor-controlled LangGraph flow
- Validate employee profile data with an Intake Agent
- Generate structured onboarding tasks with a Task Planning Agent
- Fall back to deterministic default tasks when LLM generation fails
- View generated tasks, owners, priorities, approval flags, and task metrics
- Track employee onboarding lifecycle status such as `PENDING`, `PLAN_READY`, and `FAILED`

## Tech Stack

- Frontend: Streamlit
- Backend: FastAPI
- Workflow orchestration: LangGraph
- LLM provider: OpenRouter
- Database: SQLite
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
SQLite Database
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
Tasks are saved to SQLite
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
```

Initialize the database:

```bash
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
- Phase 1 scope discipline with roadmap items separated from implemented behavior

## Roadmap

These are intentionally deferred beyond Phase 1:

- Policy and Knowledge Agent
- Approval workflow
- Welcome email draft review
- Task status editing
- Audit logs and workflow run persistence
- Calendar and manager follow-up agents
- Authentication and role-based access
- Deployment to a hosted environment

## Repository Structure

```text
agents/      LangGraph agent logic and workflow state
backend/     FastAPI app and routes
database/    SQLite schema and repositories
docs/        Architecture, API, workflow, and portfolio documentation
frontend/    Streamlit dashboard
llm/         OpenRouter client
schemas/     Pydantic request/response models
scripts/     Local workflow utilities
tests/       Agent and workflow safety tests
```
