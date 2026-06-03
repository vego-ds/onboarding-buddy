# Agents

## Implemented Agents

Onboarding Buddy currently implements three agents in the LangGraph workflow.

### Supervisor Agent

Location:

```text
agents/supervisor/
```

Responsibilities:

- choose the next workflow step
- keep routing constrained to known agents
- fall back to deterministic routing when LLM routing fails
- complete the workflow after validated tasks exist

Allowed routes:

```text
intake_agent
task_planning_agent
complete
failure_handler
```

### Intake Agent

Location:

```text
agents/intake/
```

Responsibilities:

- validate required employee fields
- mark `employee_validated`
- write intake result into workflow state
- stop downstream task planning if required employee data is missing

### Task Planning Agent

Location:

```text
agents/task_planning/
```

Responsibilities:

- generate six structured onboarding tasks through OpenRouter
- validate task shape, priority, owner, approval flags, and duplicate task names
- fall back to deterministic default tasks if LLM output is invalid or unavailable
- persist tasks
- create approval records for approval-required tasks
- create linear task dependencies
- write audit events

## Workflow State

Shared workflow state is defined in:

```text
agents/shared/workflow_state.py
```

Important state fields include:

- `workflow_run_id`
- `employee_id`
- `employee_validated`
- `onboarding_tasks`
- `approval_records`
- `task_dependencies`
- `current_agent`
- `next_agent`
- `workflow_status`
- `failure_reason`
- `agent_outputs`
- `agent_execution_history`

## Persistence and Observability

Agent execution is persisted after each onboarding workflow run:

- `workflow_runs` stores workflow-level execution state
- `agent_runs` stores individual agent execution summaries
- `audit_logs` stores workflow timeline events

The frontend Operations workspace reads these records through FastAPI workflow observability endpoints.

## Not Implemented Yet

These agents or capabilities are roadmap-only:

- Policy/Knowledge Agent
- Knowledge Agent
- Compliance Agent
- Risk Agent
- Calendar Agent
- Manager Follow-up Agent
- email drafting or sending
- Slack or Microsoft Teams notifications
- RAG/vector-memory retrieval

The current implementation deliberately keeps the active graph small: Supervisor, Intake, and Task Planning only.
