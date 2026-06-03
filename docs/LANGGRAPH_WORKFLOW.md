# LangGraph Workflow

## Current Graph

The implemented graph is intentionally small and controlled:

```text
supervisor
  |
  +--> intake_agent
  |       |
  |       v
  |    supervisor
  |
  +--> task_planning_agent
  |       |
  |       v
  |    supervisor
  |
  +--> END
```

Implemented nodes:

- `supervisor`
- `intake_agent`
- `task_planning_agent`

Roadmap nodes such as Policy/Knowledge, Calendar, Manager Follow-up, and notifications are not wired into the graph yet.

## Routing Rules

The Supervisor Agent chooses from:

```text
intake_agent
task_planning_agent
complete
failure_handler
```

Deterministic guardrails override unsafe or invalid LLM routing:

- missing validation routes to `intake_agent`
- validated employee with no tasks routes to `task_planning_agent`
- validated employee with tasks routes to `complete`
- failure reason routes to `failure_handler`

## Workflow Run Lifecycle

1. Backend receives `POST /employees/{employee_id}/generate-onboarding-plan`.
2. Backend creates a `workflow_runs` record.
3. Initial state receives `workflow_run_id`.
4. LangGraph invokes the Supervisor Agent.
5. Intake validates employee fields.
6. Task Planning generates or reuses tasks.
7. Task Planning creates approvals and dependencies.
8. Backend persists agent execution history into `agent_runs`.
9. Backend completes the workflow run.
10. Employee status updates to `PLAN_READY` when tasks exist or `FAILED` when the workflow fails.

## Task Planning Behavior

The Task Planning Agent expects six tasks. It validates:

- `task_name`
- `task_description`
- `task_priority`
- `approval_required`
- `assigned_owner`
- duplicate task names

If OpenRouter is unavailable or returns invalid data, the agent uses deterministic fallback tasks.

## Dependency and Approval Behavior

Task dependencies are created linearly after task generation. Downstream tasks cannot move to `In Progress` until upstream dependencies are `Completed`.

Approval-required tasks cannot move to `In Progress` until their approval is `Approved`.

When blockers clear, blocked tasks can unlock back to `Pending`.

## Observability

The workflow persists:

- workflow run records
- agent run summaries
- audit timeline events
- approval operations
- task status transitions
- dependency lock/unlock events

These are visible through the Operations workspace and workflow-run APIs.
