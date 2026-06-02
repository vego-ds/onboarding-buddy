# Onboarding Buddy API Design

## 1. API Design Goal

The API layer allows the Streamlit frontend to communicate with the FastAPI backend.

The API design supports:

* employee onboarding creation
* supervisor-based multi-agent workflow triggering
* onboarding checklist generation
* welcome email draft generation
* approval handling
* task status updates
* dashboard metrics
* audit log retrieval
* agent run visibility
* workflow state inspection

The API should keep the frontend separate from database logic, LangGraph internals, and direct agent execution.

The frontend should request outcomes. The backend should control how those outcomes are produced.

---

## 2. API Design Principles

* APIs should be simple and predictable.
* APIs should validate all incoming data.
* APIs should return structured responses.
* APIs should return clear error messages.
* APIs should trigger audit logging for important actions.
* APIs should not expose unnecessary employee data.
* APIs should hide internal LangGraph implementation details unless observability requires safe exposure.
* APIs should expose readable workflow status and agent activity.
* APIs should not allow the frontend to directly invoke arbitrary agents.
* APIs should route workflow requests through controlled backend services.

---

## 3. Base URL

For local development:

```text
http://localhost:8000
```

---

## 4. API Endpoints Overview

| Method | Endpoint                                          | Purpose                                       |
| ------ | ------------------------------------------------- | --------------------------------------------- |
| POST   | /employees                                        | Create employee onboarding record             |
| GET    | /employees                                        | List recent employee onboarding records       |
| GET    | /employees/{employee_id}                          | Get employee details                          |
| PUT    | /employees/{employee_id}                          | Edit employee onboarding details              |
| GET    | /employees/{employee_id}/tasks                    | Get generated onboarding tasks                |
| GET    | /employees/{employee_id}/timeline                 | Get employee workflow history                 |
| POST   | /employees/{employee_id}/generate-onboarding-plan | Trigger Supervisor Agent workflow             |
| POST   | /employees/{employee_id}/generate-checklist       | Generate onboarding checklist                 |
| POST   | /employees/{employee_id}/generate-email-draft     | Generate welcome email draft                  |
| POST   | /approvals                                        | Submit approval decision                      |
| GET    | /approvals                                        | List approval requests                        |
| PATCH  | /approvals/{approval_id}                          | Record approval decision                      |
| GET    | /tasks/{task_id}                                  | Get onboarding task                           |
| GET    | /tasks/{task_id}/dependencies                     | Get task dependencies                         |
| PATCH  | /tasks/{task_id}/status                           | Update task status                            |
| GET    | /employees/{employee_id}/status                   | Get onboarding status                         |
| GET    | /dashboard                                        | Get dashboard summary                         |
| GET    | /audit-logs                                       | Get audit logs                                |
| GET    | /agent-runs                                       | Get agent execution history                   |
| GET    | /employees/{employee_id}/agent-runs               | Get employee-specific agent execution history |
| GET    | /workflow-runs/{workflow_run_id}                  | Get workflow run details                      |
| GET    | /workflow-runs                                    | List workflow runs                            |

Current implementation supports `POST /employees`, `GET /employees`, `GET /employees/{employee_id}`, `PUT /employees/{employee_id}`, `GET /employees/{employee_id}/tasks`, `GET /employees/{employee_id}/timeline`, `POST /employees/{employee_id}/generate-onboarding-plan`, `GET /approvals`, `PATCH /approvals/{approval_id}`, `GET /tasks/{task_id}`, `GET /tasks/{task_id}/dependencies`, `PATCH /tasks/{task_id}/status`, `GET /workflow-runs`, and `GET /workflow-runs/{workflow_run_id}`. Email drafts remain a roadmap item.

---

## 5. Create Employee

### Endpoint

```http
POST /employees
```

### Purpose

Create a new employee onboarding record.

### Request Body

```json
{
  "employee_name": "Priya Sharma",
  "employee_email": "priya@company.com",
  "role": "Data Analyst",
  "department": "Analytics",
  "joining_date": "2026-06-15"
}
```

### Response

```json
{
  "employee_id": "EMP_001",
  "status": "created",
  "message": "Employee onboarding record created successfully."
}
```

---

## 6. Get Employee Details

### Endpoint

```http
GET /employees/{employee_id}
```

### Purpose

Retrieve employee onboarding details.

### Response

```json
{
  "employee_id": "EMP_001",
  "employee_name": "Priya Sharma",
  "employee_email": "priya@company.com",
  "role": "Data Analyst",
  "department": "Analytics",
  "joining_date": "2026-06-15",
  "onboarding_status": "IN_PROGRESS"
}
```

---

## 7. Generate Onboarding Plan

### Endpoint

```http
POST /employees/{employee_id}/generate-onboarding-plan
```

### Purpose

Trigger the supervisor-based multi-agent workflow.

This endpoint should start the controlled LangGraph orchestration flow:

```text
Supervisor Agent
↓
Intake Agent
↓
Policy and Knowledge Agent
↓
Task Planning Agent
```

The frontend should not directly call specialist agents. The backend starts the workflow, and the Supervisor Agent coordinates the specialist agents.

### Response

```json
{
  "employee_id": "EMP_001",
  "workflow_run_id": "WF_001",
  "workflow_status": "Running",
  "current_agent": "Supervisor Agent",
  "message": "Multi-agent onboarding workflow started successfully."
}
```

---

## 8. Generate Checklist

### Endpoint

```http
POST /employees/{employee_id}/generate-checklist
```

### Purpose

Generate onboarding tasks through the controlled workflow.

In the multi-agent version, this endpoint should usually delegate to the Supervisor Agent instead of directly calling a checklist generator.

### Response

```json
{
  "employee_id": "EMP_001",
  "workflow_run_id": "WF_001",
  "status": "checklist_generated",
  "generated_by_agent": "Task Planning Agent",
  "tasks": [
    {
      "task_id": "TASK_001",
      "task_name": "Send welcome email",
      "task_status": "Pending",
      "approval_required": true
    },
    {
      "task_id": "TASK_002",
      "task_name": "Schedule orientation",
      "task_status": "Pending",
      "approval_required": true
    }
  ]
}
```

---

## 9. Generate Welcome Email Draft

### Endpoint

```http
POST /employees/{employee_id}/generate-email-draft
```

### Purpose

Generate a welcome email draft for HR review.

The generated draft must remain subject to HR approval before official sending or simulated sending.

### Response

```json
{
  "employee_id": "EMP_001",
  "workflow_run_id": "WF_001",
  "email_draft_id": "EMAIL_001",
  "approval_status": "Awaiting Approval",
  "generated_by": "Supervisor-controlled workflow",
  "subject": "Welcome to the Team",
  "body": "Dear Priya, welcome to the Analytics team..."
}
```

---

## 10. Submit Approval Decision

### Endpoint

```http
POST /approvals
```

### Purpose

Submit HR approval, rejection, or revision request.

### Request Body

```json
{
  "employee_id": "EMP_001",
  "related_task_id": "TASK_001",
  "action_type": "welcome_email",
  "approval_status": "Approved",
  "reviewed_by": "HR Executive",
  "review_notes": "Approved after review."
}
```

### Response

```json
{
  "approval_id": "APPROVAL_001",
  "status": "approved",
  "message": "Approval decision saved successfully."
}
```

---

## 11. Update Task Status

### Endpoint

```http
PATCH /tasks/{task_id}/status
```

### Purpose

Update onboarding task status.

### Request Body

```json
{
  "task_status": "Completed"
}
```

### Response

```json
{
  "task_id": "TASK_001",
  "task_status": "Completed",
  "message": "Task status updated successfully."
}
```

---

## 12. Get Employee Onboarding Status

### Endpoint

```http
GET /employees/{employee_id}/status
```

### Purpose

Retrieve employee onboarding progress.

### Response

```json
{
  "employee_id": "EMP_001",
  "employee_name": "Priya Sharma",
  "workflow_run_id": "WF_001",
  "workflow_status": "Running",
  "current_agent": "Supervisor Agent",
  "next_agent": "Task Planning Agent",
  "completed_tasks": 2,
  "pending_tasks": 4,
  "failed_tasks": 0,
  "approval_status": "Awaiting Approval"
}
```

---

## 13. Get Dashboard Summary

### Endpoint

```http
GET /dashboard
```

### Purpose

Retrieve overall onboarding dashboard metrics.

### Response

```json
{
  "total_onboarding_cases": 10,
  "pending_tasks": 18,
  "completed_tasks": 42,
  "failed_actions": 2,
  "pending_approvals": 5,
  "active_workflows": 3,
  "failed_workflows": 1
}
```

---

## 14. Get Audit Logs

### Endpoint

```http
GET /audit-logs
```

### Purpose

Retrieve recent system and agent activity.

### Response

```json
{
  "logs": [
    {
      "log_id": "LOG_001",
      "employee_id": "EMP_001",
      "workflow_run_id": "WF_001",
      "event_type": "SUPERVISOR_ROUTED_TO_TASK_PLANNING",
      "event_message": "Supervisor Agent routed workflow to Task Planning Agent.",
      "agent_name": "Supervisor Agent",
      "routing_reason": "Employee data was validated and policy context was available.",
      "timestamp": "2026-06-01T10:30:00"
    }
  ]
}
```

---

## 15. Get Agent Runs

### Endpoint

```http
GET /agent-runs
```

### Purpose

Retrieve recent agent execution history.

This endpoint supports observability and debugging.

### Response

```json
{
  "agent_runs": [
    {
      "agent_run_id": "AR_001",
      "workflow_run_id": "WF_001",
      "employee_id": "EMP_001",
      "agent_name": "Task Planning Agent",
      "agent_role": "TaskPlanning",
      "execution_status": "Success",
      "routing_reason": "Employee profile and policy context were ready for checklist generation.",
      "retry_count": 0,
      "execution_duration_ms": 1240,
      "llm_provider": "OpenRouter",
      "llm_model": "openai/gpt-4.1",
      "started_at": "2026-06-01T10:30:00",
      "completed_at": "2026-06-01T10:30:01"
    }
  ]
}
```

---

## 16. Get Employee Agent Runs

### Endpoint

```http
GET /employees/{employee_id}/agent-runs
```

### Purpose

Retrieve agent execution history for a specific employee onboarding workflow.

### Response

```json
{
  "employee_id": "EMP_001",
  "agent_runs": [
    {
      "agent_run_id": "AR_001",
      "workflow_run_id": "WF_001",
      "agent_name": "Intake Agent",
      "agent_role": "Intake",
      "execution_status": "Success",
      "output_summary": "Employee profile validation completed successfully.",
      "retry_count": 0
    },
    {
      "agent_run_id": "AR_002",
      "workflow_run_id": "WF_001",
      "agent_name": "Policy and Knowledge Agent",
      "agent_role": "PolicyAndKnowledge",
      "execution_status": "Success",
      "output_summary": "Role-based onboarding context retrieved.",
      "retry_count": 0
    }
  ]
}
```

---

## 17. Get Workflow Run Details

### Endpoint

```http
GET /workflow-runs/{workflow_run_id}
```

### Purpose

Retrieve details for a specific workflow run.

### Response

```json
{
  "workflow_run_id": "WF_001",
  "employee_id": "EMP_001",
  "workflow_status": "Running",
  "current_node": "Supervisor Routing Node",
  "current_agent": "Supervisor Agent",
  "next_agent": "Task Planning Agent",
  "retry_count": 0,
  "failure_reason": null,
  "llm_provider": "OpenRouter",
  "llm_model": "openai/gpt-4.1",
  "started_at": "2026-06-01T10:29:58",
  "completed_at": null
}
```

---

## 18. Error Response Format

All API errors should follow a consistent structure.

```json
{
  "error": true,
  "error_type": "VALIDATION_ERROR",
  "message": "Employee email is required."
}
```

---

## 19. Common Error Types

| Error Type            | Meaning                                       |
| --------------------- | --------------------------------------------- |
| VALIDATION_ERROR      | Required input is missing or invalid          |
| NOT_FOUND             | Requested record does not exist               |
| WORKFLOW_ERROR        | LangGraph workflow failed                     |
| ROUTING_ERROR         | Supervisor Agent routing failed               |
| AGENT_EXECUTION_ERROR | Specialist agent execution failed             |
| TOOL_EXECUTION_ERROR  | Tool execution failed                         |
| DATABASE_ERROR        | Database operation failed                     |
| LLM_PROVIDER_ERROR    | OpenRouter or configured model request failed |

---

## 20. API Security Notes

For MVP:

* authentication can be deferred
* input validation is mandatory
* sensitive actions must require approval
* APIs should not expose unnecessary employee data
* APIs should not allow direct arbitrary agent invocation
* OpenRouter API keys must remain in environment variables
* agent logs should avoid raw secrets and sensitive credential values

Future versions should include:

* authentication
* role-based access control
* rate limiting
* audit retention policies

---

## 21. API Design Summary

The API layer acts as the controlled communication boundary between the frontend, backend, database, and LangGraph multi-agent workflow.

The API design prioritizes:

* clarity
* validation
* observability
* safe workflow triggering
* supervisor-controlled orchestration
* future frontend flexibility

The API should expose enough information for HR users and developers to understand workflow progress, while hiding unnecessary internal implementation complexity.
