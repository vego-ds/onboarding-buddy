# API Design

## Purpose

The FastAPI backend is the only API surface the Streamlit frontend uses. The frontend does not call agents directly.

The API currently supports:

- employee record management
- onboarding workflow execution
- task lifecycle management
- approval operations
- task dependency enforcement visibility
- employee timeline events
- workflow run and agent run observability

## Base URL

Local development:

```text
http://127.0.0.1:8000
```

Streamlit Cloud should set `API_BASE_URL` to the deployed Render backend URL.

## Implemented Endpoints

### Health

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Backend health check |

### Employees

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/employees` | List employee records |
| `POST` | `/employees` | Create employee onboarding record |
| `GET` | `/employees/{employee_id}` | Get employee detail |
| `PUT` | `/employees/{employee_id}` | Edit employee detail |
| `GET` | `/employees/{employee_id}/tasks` | Get employee task summary and tasks |
| `GET` | `/employees/{employee_id}/timeline` | Get employee workflow timeline |
| `POST` | `/employees/{employee_id}/generate-onboarding-plan` | Run the LangGraph onboarding workflow |

### Tasks

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/tasks/{task_id}` | Get task detail and enforcement state |
| `GET` | `/tasks/{task_id}/dependencies` | Get upstream dependencies and locked/unlocked state |
| `PATCH` | `/tasks/{task_id}/status` | Update task status |

Valid task statuses:

```text
Pending
In Progress
Completed
Blocked
Failed
```

When a task is locked by an approval or unfinished upstream dependency, the API prevents moving it to `In Progress`. A premature start attempt marks the task `Blocked` and writes a timeline event.

### Approvals

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/approvals` | List approvals, optionally filtered by employee or status |
| `GET` | `/approvals/{approval_id}` | Get approval detail |
| `PATCH` | `/approvals/{approval_id}` | Record approval decision |

Valid approval statuses:

```text
Awaiting Approval
Approved
Rejected
Revision Requested
```

When an approval is marked `Approved`, the related task is re-evaluated. If all blockers are clear, a blocked task unlocks back to `Pending`.

### Workflow Runs

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/workflow-runs` | List workflow runs |
| `GET` | `/workflow-runs/{workflow_run_id}` | Get workflow run detail and agent run history |

Workflow run IDs are normalized before lookup, so lowercase path values still resolve.

## Important Response Shapes

### `POST /employees`

```json
{
  "employee_id": "EMP_12345678",
  "status": "created",
  "message": "Employee onboarding record created successfully.",
  "employee": {
    "employee_id": "EMP_12345678",
    "employee_name": "Sarah Chen",
    "employee_email": "sarah.chen@company.com",
    "role": "Data Engineer",
    "department": "Platform Engineering",
    "joining_date": "2026-07-01",
    "onboarding_status": "PENDING"
  }
}
```

Duplicate employee emails return `409`.

### `POST /employees/{employee_id}/generate-onboarding-plan`

```json
{
  "employee_id": "EMP_12345678",
  "workflow_run_id": "WF_12345678",
  "workflow_status": "COMPLETED",
  "next_agent": "complete",
  "routing_reason": "Employee is validated and onboarding tasks exist. Workflow can complete.",
  "task_count": 6,
  "approval_required_count": 4,
  "approval_count": 4,
  "tasks": []
}
```

### `GET /tasks/{task_id}/dependencies`

```json
{
  "task_id": "TASK_12345678",
  "dependency_count": 1,
  "dependencies": [],
  "is_locked": true,
  "can_start": false,
  "lock_reasons": [
    "Collect employee documents is Pending"
  ],
  "enforcement": {
    "task_id": "TASK_12345678",
    "is_locked": true,
    "can_start": false,
    "lock_reasons": []
  }
}
```

### `GET /workflow-runs/{workflow_run_id}`

```json
{
  "workflow_run_id": "WF_12345678",
  "employee_id": "EMP_12345678",
  "workflow_status": "COMPLETED",
  "started_at": "2026-06-03T00:00:00+00:00",
  "completed_at": "2026-06-03T00:01:00+00:00",
  "workflow_run": {},
  "agent_run_count": 2,
  "agent_runs": []
}
```

## Not Implemented Yet

These are roadmap items and should not be documented as active API endpoints:

- `POST /employees/{employee_id}/generate-checklist`
- `POST /employees/{employee_id}/generate-email-draft`
- `GET /dashboard`
- `GET /audit-logs`
- `GET /agent-runs`
- `GET /employees/{employee_id}/agent-runs`
- authentication or role-based access endpoints
- notification endpoints
