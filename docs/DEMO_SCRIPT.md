# Demo Script

## Goal

Show that Onboarding Buddy is a usable Phase 1 AI workflow product, not just an agent experiment.

## Setup

```bash
source venv/bin/activate
uvicorn backend.main:app --reload
streamlit run frontend/app.py
```

## Recording Flow

1. Open the Streamlit app.
2. Show the dashboard metrics and API status indicator.
3. Create a new employee:
   - Name: `Sarah Chen`
   - Email: `sarah.chen@company.com`
   - Role: `Data Engineer`
   - Department: `Platform Engineering`
   - Joining date: choose a future date
4. Show the generated employee ID and recent employee card.
5. Go to Generate Plan.
6. Select the employee from the dropdown.
7. Generate the onboarding plan.
8. Show the task metrics:
   - total tasks
   - high priority tasks
   - approval-required tasks
   - owners
9. Expand workflow details and briefly point out supervisor routing and agent output.
10. Go to Operations.
11. Show the approval queue for approval-required tasks.
12. Show the task status controls for the same employee.
13. Point out dependency labels under each task.
14. Show the workflow timeline.
15. Show the recent workflow run and agent execution summaries.
16. Go to Tasks.
17. Fetch tasks for the same employee to show persistence.
18. End on the Directory tab to show the product-style dashboard view.

## Talking Points

- The frontend never calls agents directly; it calls the FastAPI backend.
- The backend triggers a LangGraph workflow.
- The Supervisor Agent controls routing.
- Intake validates employee data before task planning.
- Task Planning generates structured tasks and validates them before persistence.
- The system falls back to deterministic tasks if LLM generation fails.
- Phase 2 starts with approval operations and task status updates.
- Dependency enforcement prevents downstream work from starting too early.
- Audit events make the workflow explainable.
- Workflow-run records make execution observable.
- Policy retrieval, email drafts, and manager follow-up automation remain future roadmap items.
