# Demo Script

## Goal

Show Onboarding Buddy as an AI workflow operations MVP with a first Phase 3 approved-source onboarding assistant, not just a task-generation demo.

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
17. Open Assistant.
18. Ask an onboarding question with HR or IT role context.
19. Show the source-backed answer, confidence score, citation cards, and sources expander.
20. Optionally show the knowledge reindex control.
21. End on the Directory tab.

## Talking Points

- FastAPI controls workflow execution; the frontend does not call agents directly.
- LangGraph routes through Supervisor, Intake, and Task Planning.
- OpenRouter is used for LLM generation, with deterministic fallback tasks for reliability.
- Workflow runs and agent runs are persisted for observability.
- Approval decisions and dependency completion affect task lock state.
- Timeline events make workflow behavior auditable.
- PostgreSQL is the runtime database.
- The assistant uses approved local knowledge and optional workflow context.
- The assistant uses a PostgreSQL-backed chunk index with deterministic local embeddings.
- The assistant is not yet a production security boundary or external embedding pipeline.

## Roadmap Callout

The demo should not claim these are implemented:

- Policy/Knowledge Agent
- external embedding provider integration
- pgvector or managed vector database migration
- real email or Slack notifications
- authentication and authorization
- RBAC enforcement
- background workers
- Alembic migrations
