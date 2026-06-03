# Demo Script

## Goal

Show Onboarding Buddy as a Phase 2 AI workflow operations MVP, not just a task-generation demo.

## Setup

```bash
source venv/bin/activate
uvicorn backend.main:app --reload
streamlit run frontend/app.py
```

## Recording Flow

1. Open the Streamlit app.
2. Show dashboard metrics and API status.
3. Create a new employee.
4. Confirm the employee appears in Recent Employees and Directory.
5. Generate an onboarding plan for that employee.
6. Show the returned `workflow_run_id`.
7. Review generated tasks, owners, priorities, and approval flags.
8. Open Operations.
9. Show the approval queue.
10. Show locked/unlocked task indicators.
11. Try to start a locked downstream task and show the backend enforcement message.
12. Approve the relevant approval.
13. Complete the upstream task.
14. Show the downstream task unlocking.
15. Show the employee workflow timeline.
16. Show Recent Workflow Runs and agent execution summaries.
17. End on the Directory tab.

## Talking Points

- FastAPI controls workflow execution; the frontend does not call agents directly.
- LangGraph routes through Supervisor, Intake, and Task Planning.
- OpenRouter is used for LLM generation, with deterministic fallback tasks for reliability.
- Workflow runs and agent runs are persisted for observability.
- Approval decisions and dependency completion affect task lock state.
- Timeline events make workflow behavior auditable.
- PostgreSQL is supported for Phase 2 deployment, with SQLite available for local fallback.

## Roadmap Callout

The demo should not claim these are implemented:

- Policy/Knowledge Agent
- RAG/vector memory
- real email or Slack notifications
- authentication and authorization
- background workers
- Alembic migrations
