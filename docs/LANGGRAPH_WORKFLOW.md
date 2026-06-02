# Onboarding Buddy LangGraph Workflow Design

## 1. Workflow Goal

The LangGraph workflow is responsible for orchestrating the onboarding lifecycle from employee onboarding creation to workflow completion.

The workflow uses a supervisor-based multi-agent architecture.

The workflow manages:

* stateful onboarding execution
* Supervisor Agent routing
* specialist agent execution
* AI-generated onboarding plans
* configurable model orchestration through OpenRouter
* provider-isolated workflow execution
* human approval handling
* controlled tool execution
* workflow logging
* failure handling
* retry routing
* workflow completion tracking

The workflow is intentionally designed as a controlled and observable multi-agent workflow system rather than a fully autonomous AI agent.

---

## 2. Workflow Engineering Principles

The workflow follows these engineering principles:

* state-first orchestration
* supervisor-based routing
* specialist agent isolation
* modular node design
* human approval for sensitive actions
* controlled tool execution
* persistence-first architecture
* observability and tracing
* safe failure handling
* minimal autonomous behavior

The workflow prioritizes:

* reliability
* predictability
* maintainability
* debuggability
* routing transparency

over:

* excessive autonomy
* recursive reasoning
* uncontrolled agent execution
* uncontrolled agent spawning

---

## 3. Multi-Agent Workflow Strategy

The workflow uses one Supervisor Agent and a small set of specialist agents.

### Current Phase 1 Agents

| Agent                      | Purpose                                           |
| -------------------------- | ------------------------------------------------- |
| Supervisor Agent           | Coordinates routing and workflow execution        |
| Intake Agent               | Validates employee onboarding information         |
| Task Planning Agent        | Generates onboarding checklist and task plan      |

The Policy and Knowledge Agent remains in the design roadmap, but it is not currently wired into the LangGraph implementation. The implemented Phase 1 graph is:

```text
Supervisor Agent
↓
Intake Agent
↓
Supervisor Agent
↓
Task Planning Agent
↓
Supervisor Agent
↓
Complete
```

### Deferred Phase 2 Agents

| Agent                   | Purpose                                |
| ----------------------- | -------------------------------------- |
| Calendar Agent          | Schedules onboarding meetings          |
| Manager Follow-up Agent | Sends manager reminders and follow-ups |

The MVP intentionally does not include every possible agent. The goal is to prove the core architecture first.

```text
Supervisor Agent
↓
MVP Specialist Agents
↓
Controlled Tools
↓
Database + Monitoring
```

---

## 4. Workflow Lifecycle

The onboarding workflow follows this execution lifecycle:

```text
Start Workflow
↓
Fetch Employee Data
↓
Supervisor Routing
↓
Intake Agent Validation
↓
Supervisor Routing
↓
Policy and Knowledge Agent Retrieval
↓
Supervisor Routing
↓
Task Planning Agent Checklist Generation
↓
Validate Agent Output
↓
Save Tasks
↓
Generate Welcome Email
↓
Wait For Approval
↓
Execute Approved Action
↓
Write Audit Logs
↓
Complete Workflow
```

Failure routes include:

* validation failure
* approval rejection
* tool execution failure
* workflow interruption
* missing data
* routing failure
* specialist agent failure
* retry exhaustion

---

## 5. Workflow State Philosophy

The workflow uses persistent state throughout execution.

The state acts as:

* workflow memory
* execution context
* routing context
* agent coordination context
* retry context
* debugging context
* observability context

The workflow should never rely entirely on:

* chat history
* raw LLM memory
* prompt continuation
* temporary in-memory state

All important workflow state must remain explicitly structured and persistable.

---

## 6. Workflow State Fields

| Field                     | Purpose                                          |
| ------------------------- | ------------------------------------------------ |
| employee_id               | Unique employee identifier                       |
| employee_name             | Employee full name                               |
| employee_email            | Employee email                                   |
| role                      | Employee role                                    |
| department                | Employee department                              |
| joining_date              | Employee joining date                            |
| onboarding_tasks          | Generated onboarding tasks                       |
| email_draft               | Generated email draft                            |
| approval_status           | Approval state                                   |
| task_status               | Workflow task state                              |
| current_node              | Current workflow node                            |
| current_agent             | Agent currently executing                        |
| next_agent                | Agent selected by Supervisor Agent               |
| supervisor_routing_reason | Reason for the Supervisor Agent routing decision |
| agent_outputs             | Structured outputs returned by specialist agents |
| agent_execution_history   | Ordered history of agent executions              |
| retry_count               | Retry tracking                                   |
| failure_reason            | Failure details                                  |
| audit_events              | Workflow event history                           |
| tool_execution_result     | Tool execution response                          |
| workflow_status           | Overall workflow status                          |
| llm_provider              | Active LLM provider                              |
| llm_model                 | Active configured model                          |

---

## 7. Agent Communication Model

Agents communicate through workflow state controlled by the Supervisor Agent.

Specialist agents do not freely call each other.

### Communication Pattern

```text
Supervisor Agent
↓
Reads Workflow State
↓
Creates Structured Agent Request
↓
Routes To Specialist Agent
↓
Specialist Agent Executes Focused Task
↓
Specialist Agent Returns Structured Output
↓
Supervisor Agent Validates Output
↓
Workflow State Updates
```

### Example Structured Agent Request

```json
{
  "target_agent": "intake_agent",
  "task_type": "validate_employee_profile",
  "employee_id": "EMP_001",
  "required_fields": [
    "employee_name",
    "employee_email",
    "role",
    "department",
    "joining_date"
  ]
}
```

### Example Structured Agent Response

```json
{
  "agent_name": "intake_agent",
  "execution_status": "success",
  "missing_fields": [],
  "validated_profile": {
    "employee_name": "Priya Sharma",
    "role": "Data Analyst",
    "department": "Analytics",
    "joining_date": "2026-06-15"
  }
}
```

---

## 8. Workflow Nodes

### 8.1 Start Node

Responsibilities:

* initialize workflow execution
* initialize workflow state
* validate employee identifier
* create workflow run record

Input:

* employee_id

Output:

* initialized workflow state

---

### 8.2 Fetch Employee Data Node

Responsibilities:

* retrieve employee onboarding record
* validate that the employee exists
* load employee fields into workflow state

Required Fields:

* employee name
* employee email
* role
* department
* joining date

Failure Conditions:

* employee not found
* missing required fields

Output:

* employee profile state

---

### 8.3 Supervisor Routing Node

Responsibilities:

* inspect current workflow state
* decide which specialist agent should run next
* record routing reason
* update current_agent and next_agent fields
* route failures to failure handling
* route approval-required actions to approval node

Input:

* current workflow state
* previous agent outputs
* retry count
* failure reason
* approval status

Output:

* selected next node or agent
* routing reason
* updated workflow state

Example routing rules:

| Condition                      | Route                           |
| ------------------------------ | ------------------------------- |
| Employee data needs validation | Intake Agent                    |
| Policy context is missing      | Policy and Knowledge Agent      |
| Checklist needs generation     | Task Planning Agent             |
| Output validation failed       | Retry relevant specialist agent |
| Approval required              | Approval Node                   |
| Tool failed                    | Failure Handling Node           |
| Workflow complete              | Complete Workflow Node          |

---

### 8.4 Intake Agent Node

Responsibilities:

* validate employee onboarding information
* detect missing required fields
* normalize employee profile data
* return structured validation output

Input:

* employee profile state

Output:

* validated employee profile
* missing fields list
* validation status

Failure Conditions:

* missing required employee data
* invalid email
* incomplete onboarding record

Failure Actions:

* stop workflow safely
* notify HR to correct employee record
* write audit log

---

### 8.5 Policy and Knowledge Agent Node

Responsibilities:

* retrieve onboarding templates
* retrieve policy context
* retrieve role-specific onboarding examples
* prepare context for task planning

Input:

* role
* department
* joining date
* company onboarding knowledge

Output:

* onboarding policy context
* role-based template
* knowledge summary

Failure Conditions:

* policy memory unavailable
* template not found
* retrieval failure

Failure Actions:

* fallback to default onboarding template
* escalate to manual review if fallback is not available

---

### 8.6 Task Planning Agent Node

Responsibilities:

* generate onboarding checklist
* generate onboarding sequence
* identify approval-required tasks
* assign suggested task ownership
* return structured task output

Input:

* validated employee profile
* policy context
* role-based onboarding template

Output:

* onboarding task list
* task priorities
* approval flags
* task ownership recommendations

Example Tasks:

* send welcome email
* collect employee documents
* schedule orientation
* assign onboarding buddy
* share company handbook

---

### 8.7 Validate Agent Output Node

Responsibilities:

* validate specialist agent outputs
* validate generated checklist structure
* remove duplicate tasks
* ensure mandatory onboarding tasks exist
* verify approval flags
* verify structured output schema

Validation Rules:

* no empty tasks
* no duplicate tasks
* no malformed structure
* mandatory onboarding steps required
* approval-required tasks must be marked
* output must match expected schema

Failure Actions:

* retry specialist agent
* escalate for manual review after retry exhaustion

---

### 8.8 Save Tasks Node

Responsibilities:

* persist onboarding tasks into SQLite
* assign task IDs
* initialize task states
* store generated_by_agent metadata
* write audit log

Default Task State:

```text
Pending
```

---

### 8.9 Generate Welcome Email Node

Responsibilities:

* generate onboarding welcome email through the OpenRouter provider layer
* use configured model routing for email generation
* personalize onboarding communication
* save draft for approval

Input:

* employee profile data
* onboarding task context
* company context

Output:

* email draft
* approval request

---

### 8.10 Approval Node

Responsibilities:

* wait for HR approval
* pause workflow execution safely
* persist approval state
* route workflow based on HR decision

Possible Approval States:

* Approved
* Rejected
* Revision Requested

Workflow Behavior:

* Approved means continue workflow
* Rejected means stop or revise workflow
* Revision Requested means regenerate content

---

### 8.11 Execute Tool Node

Responsibilities:

* invoke approved onboarding tools
* process controlled actions
* capture tool responses
* update task state
* write tool execution metadata

Possible Tool Actions:

* save email draft
* simulate email sending
* simulate orientation scheduling
* update task state
* simulate manager notification

Output:

* tool execution result

---

### 8.12 Audit Logging Node

Responsibilities:

* record workflow activity
* store audit trail
* improve observability
* persist routing and agent metadata

Logged Events:

* workflow start
* supervisor routing
* specialist agent execution
* checklist generation
* approvals
* failures
* retries
* workflow completion

---

### 8.13 Failure Handling Node

Responsibilities:

* safely handle workflow failures
* preserve failure context
* route retry logic
* escalate when retry limit is reached

Failure Examples:

* invalid specialist agent output
* Supervisor Agent routing failure
* OpenRouter request failure
* provider timeout
* malformed model response
* tool failure
* database failure
* approval timeout
* malformed task structure

Failure Actions:

* retry workflow step
* retry relevant specialist agent
* escalate for manual review
* terminate workflow safely

---

### 8.14 Complete Workflow Node

Responsibilities:

* mark onboarding workflow complete
* finalize workflow state
* write completion logs
* preserve final agent execution summary

Final Workflow States:

* Completed
* Failed
* Cancelled

---

## 9. Workflow Routing Logic

### Standard Workflow

```text
Start
→ Fetch Employee Data
→ Supervisor Routing
→ Intake Agent
→ Supervisor Routing
→ Policy and Knowledge Agent
→ Supervisor Routing
→ Task Planning Agent
→ Validate Agent Output
→ Save Tasks
→ Generate Welcome Email
→ Approval
→ Execute Tool
→ Audit Logging
→ Complete Workflow
```

---

### Missing Data Route

```text
Fetch Employee Data
→ Supervisor Routing
→ Intake Agent
→ Missing Required Data
→ Audit Logging
→ Stop Workflow
→ Request HR Correction
```

---

### Specialist Agent Failure Route

```text
Specialist Agent
→ Failure
→ Failure Handling
→ Retry Specialist Agent
→ If Retry Limit Reached
→ Manual Review
```

---

### Validation Failure Route

```text
Task Planning Agent
→ Validate Agent Output
→ Validation Failure
→ Retry Task Planning Agent
→ If Retry Limit Reached
→ Manual Review
```

---

### Approval Rejection Route

```text
Approval
→ Rejected
→ Audit Logging
→ End Workflow
```

---

### Revision Route

```text
Approval
→ Revision Requested
→ Supervisor Routing
→ Relevant Specialist Agent
→ Validate Agent Output
→ Return To Approval
```

---

### Tool Failure Route

```text
Execute Tool
→ Failure Handling
→ Retry Tool Execution
→ If Retry Limit Reached
→ Escalation
```

---

### Critical Failure Route

```text
Critical Failure
→ Capture Failure Context
→ Audit Logging
→ Preserve Workflow State
→ Stop Workflow
→ Notify HR
```

---

## 10. Conditional Routing Strategy

The Supervisor Agent controls conditional routing.

Example routing logic:

```python
def route_next_step(state):
    if state.get("failure_reason"):
        return "failure_handling"

    if not state.get("employee_id"):
        return "failure_handling"

    if not state.get("employee_validated"):
        return "intake_agent"

    if not state.get("policy_context"):
        return "policy_knowledge_agent"

    if not state.get("onboarding_tasks"):
        return "task_planning_agent"

    if not state.get("tasks_validated"):
        return "validate_agent_output"

    if state.get("approval_status") == "awaiting_approval":
        return "approval"

    if state.get("approval_status") == "approved":
        return "execute_tool"

    if state.get("workflow_status") == "completed":
        return "complete_workflow"

    return "failure_handling"
```

This function is not final implementation code. It explains how routing decisions should behave.

---

## 11. Retry Strategy

Retry logic should remain controlled and limited.

Retry principles:

* avoid infinite retries
* preserve failure context
* log retry attempts
* escalate repeated failures
* retry only the failed node or agent when possible

Recommended retry limits:

| Failure Type                               | Retry Count |
| ------------------------------------------ | ----------- |
| Specialist agent output validation failure | 2           |
| Supervisor routing failure                 | 1           |
| LLM generation failure                     | 2           |
| OpenRouter request failure                 | 2           |
| Tool execution failure                     | 2           |
| Database save failure                      | 1           |
| Validation failure                         | 2           |

After retry exhaustion:

* route workflow to manual escalation
* preserve workflow state
* write audit log
* expose failure reason to HR

---

## 12. Tool Invocation Philosophy

The configured model should never directly:

* modify database records
* trigger external systems
* bypass approval workflows
* execute unrestricted system actions

The workflow must:

* validate tool inputs
* isolate tool execution
* capture tool outputs
* record audit logs
* preserve agent source metadata

Tool invocation must remain deterministic and observable.

---

## 13. Prompt Engineering Strategy

Prompt templates should remain isolated from workflow logic.

Prompt categories:

* supervisor routing prompts
* intake validation prompts
* policy retrieval prompts
* checklist generation prompts
* email generation prompts
* validation prompts
* summarization prompts

Prompt goals:

* predictable structure
* concise outputs
* low hallucination risk
* easy debugging
* easy versioning
* structured responses

Prompt templates should remain version controlled inside:

```text
agents/prompts/
```

---

## 14. Provider Abstraction Strategy

The workflow is intentionally designed to remain provider-agnostic.

OpenRouter acts as the model routing and provider abstraction layer.

Benefits:

* configurable model routing
* reduced vendor lock-in
* easier provider replacement
* centralized provider configuration
* consistent workflow behavior across models

The orchestration layer should avoid direct dependency on:

* provider-specific SDK behavior
* provider-specific response formats
* provider-specific workflow assumptions

Future providers may include:

* direct OpenAI
* Azure OpenAI
* Anthropic
* local models
* enterprise-hosted models

The workflow should preserve:

* provider metadata
* configured model metadata
* request failure metadata
* retry metadata

for observability and debugging.

---

## 15. Workflow Observability

The workflow should support:

* LangSmith tracing
* audit logs
* backend logs
* retry visibility
* node transition visibility
* workflow status visibility
* provider request failures
* configured model metadata
* provider retry visibility
* supervisor routing visibility
* specialist agent execution history

Important observable events:

* node execution
* supervisor routing
* specialist agent execution
* retries
* failures
* approvals
* workflow completion

Observability is considered a mandatory engineering requirement.

---

## 16. Persistence Strategy

The workflow must persist important execution data.

Persisted data includes:

* workflow run status
* current node
* current agent
* next agent
* supervisor routing reason
* retry count
* failure reason
* approval state
* agent execution history
* onboarding tasks
* tool execution result

Persistence should support:

* approval pauses
* retry recovery
* backend restarts
* workflow inspection
* debugging

---

## 17. Engineering Constraints

The MVP intentionally avoids:

* recursive autonomous agents
* uncontrolled tool access
* excessive multi-agent systems
* dynamic self-modifying prompts
* autonomous approval bypassing
* provider-specific workflow coupling
* unmanaged parallel agent execution

The workflow is intentionally designed as:

* controlled
* stateful
* observable
* modular
* production-aware
* supervisor-routed

rather than experimental autonomous AI.

---

## 18. Workflow Design Summary

The LangGraph workflow acts as:

* multi-agent orchestrator
* workflow state manager
* supervisor routing engine
* specialist agent execution coordinator
* approval pause manager
* controlled tool execution layer
* observability layer

The architecture prioritizes:

* reliability
* engineering clarity
* maintainability
* debugging simplicity
* future scalability
* routing transparency
* safe execution

This workflow design is suitable for:

* AI engineering portfolios
* workflow automation systems
* enterprise AI MVPs
* human-in-the-loop AI systems
* supervisor-based multi-agent systems
