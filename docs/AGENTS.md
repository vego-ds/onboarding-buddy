# Onboarding Buddy System Architecture

## 1. Architecture Overview

Onboarding Buddy follows a layered, supervisor-based multi-agent architecture.

The system is designed around one central orchestration agent and multiple specialist agents.

```text
HR User
↓
Streamlit Frontend
↓
FastAPI Backend
↓
LangGraph Multi-Agent Orchestration
↓
Supervisor Agent
↓
Specialist Agents
↓
Tool Layer + Memory Layer
↓
SQLite Database + ChromaDB Memory + Monitoring
```

The Supervisor Agent coordinates the onboarding workflow. Specialist agents perform focused jobs such as validating employee information, retrieving policy knowledge, and generating onboarding tasks.

This architecture avoids putting all responsibilities into one large AI agent. Instead, the system separates work into smaller, easier-to-debug agent roles.


## 2. Core Components

### Frontend Layer

The frontend is built using Streamlit.

It allows HR users to:

- enter employee details
- generate onboarding workflows
- review onboarding tasks
- approve AI-generated actions
- monitor onboarding progress
- inspect agent activity logs
- view workflow failures and retry states

The frontend does not directly call agents. It communicates only with the FastAPI backend.


### Backend Layer

The backend is built using FastAPI.

It handles:

- API requests
- input validation
- workflow triggers
- database writes
- approval decisions
- dashboard data retrieval
- communication with the LangGraph orchestration layer

The backend acts as the controlled entry point into the multi-agent workflow.


### LangGraph Multi-Agent Orchestration Layer

The multi-agent workflow is built using LangGraph.

LangGraph manages:

- workflow state
- agent routing
- execution order
- retries
- approval pauses
- tool execution
- failure routing
- audit logging
- monitoring traces

LangGraph is used because onboarding is not just one prompt and one response. It is a stateful workflow with multiple steps, decisions, approvals, and failures.


### Supervisor Agent

The Supervisor Agent is the central coordinator.

It does not do every task itself. Instead, it decides which specialist agent should handle each part of the workflow.

The Supervisor Agent is responsible for:

- receiving workflow requests from the backend
- reading workflow state
- deciding the next agent to call
- routing work to specialist agents
- checking whether required data is missing
- coordinating task generation
- collecting specialist outputs
- deciding when human approval is required
- updating workflow state
- routing failures to safe handling paths
- producing final workflow summaries

Simple explanation:

The Supervisor Agent is like the class teacher. It does not do every student’s homework. It gives the right work to the right student, checks the result, and keeps the class organized.


### Specialist Agent Layer

Specialist agents perform focused jobs.

The MVP includes:

- Intake Agent
- Policy and Knowledge Agent
- Task Planning Agent

Phase 2 adds:

- Calendar Agent
- Manager Follow-up Agent

Each specialist agent has a narrow responsibility. This keeps the workflow modular and easier to debug.


### Intake Agent

The Intake Agent validates employee onboarding information.

It is responsible for:

- checking if required employee fields are present
- detecting missing joining date, role, email, department, or manager information
- normalizing employee data
- preparing clean employee context for other agents
- returning validation results to the Supervisor Agent

Example:

If HR forgets to enter the joining date, the Intake Agent flags the missing field before the workflow continues.


### Policy and Knowledge Agent

The Policy and Knowledge Agent retrieves onboarding knowledge.

It is responsible for:

- searching onboarding templates
- retrieving company policy information
- checking onboarding rules
- supporting role-based onboarding recommendations
- answering onboarding-related questions
- grounding generated outputs in stored knowledge

For the MVP, this agent can use static templates and ChromaDB memory. In future versions, it can connect to real HR policy documents.


### Task Planning Agent

The Task Planning Agent generates onboarding task plans.

It is responsible for:

- creating onboarding checklists
- recommending task order
- identifying missing onboarding steps
- marking which tasks require approval
- creating structured task output for the database
- preparing task plans for HR review

Example tasks:

- Send welcome email
- Schedule orientation
- Request identity documents
- Assign onboarding buddy
- Share company handbook
- Prepare role-specific setup tasks


### Deferred Phase 2 Agents

The following agents are intentionally deferred to Phase 2.

#### Calendar Agent

Responsible for:

- scheduling orientation
- suggesting meeting times
- creating simulated or real calendar events
- coordinating onboarding sessions

#### Manager Follow-up Agent

Responsible for:

- notifying hiring managers
- sending follow-up reminders
- tracking manager-owned tasks
- escalating delayed onboarding items

These are deferred because building all agents immediately would overcomplicate the MVP.


### OpenRouter LLM Provider Layer

The LLM provider layer uses OpenRouter to route requests to configurable language models.

The selected model is managed through environment variables. This allows the system to switch between supported OpenRouter models without changing core workflow logic.

The OpenRouter layer supports:

- supervisor reasoning
- specialist agent responses
- onboarding checklist generation
- welcome email drafting
- task recommendations
- agent decision summaries
- structured workflow outputs

Recommended configuration:

```text
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=openai/gpt-4.1
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```


### Tool Layer

The tool layer contains controlled functions used by the multi-agent workflow.

In Version 1, tools are simulated instead of using real enterprise integrations.

Planned tools:

- Checklist Tool
- Email Draft Tool
- Approval Tool
- Task Status Tool
- Audit Log Tool
- Calendar Simulation Tool
- Notification Simulation Tool

Agents do not directly modify the database without controlled tool logic. Tools protect the system from unsafe or unvalidated actions.


### Data Layer

SQLite stores structured workflow data.

It stores:

- employee records
- onboarding tasks
- approvals
- audit logs
- agent runs
- workflow state
- retry metadata
- provider metadata
- model metadata

ChromaDB may be used for vector memory, including:

- onboarding templates
- FAQ content
- company policy snippets
- role-based onboarding examples


### Monitoring Layer

Monitoring includes:

- Python backend logs
- SQLite audit logs
- LangSmith traces
- agent execution records
- supervisor routing history
- specialist agent results
- OpenRouter request metadata

Monitoring is critical because multi-agent systems need clear visibility. Developers must be able to answer:

- Which agent ran?
- Why was that agent selected?
- What did the agent return?
- Did the output pass validation?
- Did the tool execute successfully?
- Where did the workflow fail?


## 3. Multi-Agent Architecture Strategy

### Strategy Goal

The goal is to build a multi-agent onboarding system without overcomplicating the MVP.

The system uses:

```text
1 Supervisor Agent
+
3 MVP Specialist Agents
```

This gives the project strong architecture while keeping implementation realistic.


### MVP Agents

| Agent                      | Purpose                                      |
| -------------------------- | -------------------------------------------- |
| Supervisor Agent           | Routes and coordinates the workflow          |
| Intake Agent               | Validates employee onboarding data           |
| Policy and Knowledge Agent | Retrieves policy and onboarding knowledge    |
| Task Planning Agent        | Generates onboarding checklist and task plan |


### Deferred Agents

| Agent                   | Phase   | Reason Deferred                                     |
| ----------------------- | ------- | --------------------------------------------------- |
| Calendar Agent          | Phase 2 | Real calendar logic adds complexity                 |
| Manager Follow-up Agent | Phase 2 | Manager reminder workflows are not required for MVP |


### Why Not Build All Agents Immediately

Building too many agents in the MVP would create:

- more routing complexity
- more bugs
- harder testing
- unclear debugging
- more database fields
- more edge cases
- slower delivery

The MVP should prove the core idea first:

```text
Supervisor Agent routes work to focused specialist agents.
```

Once that works, Phase 2 can add more operational agents.


## 4. Data Flow

### High-Level Data Flow

1. HR enters employee details in the Streamlit UI.
2. Streamlit sends the employee data to the FastAPI backend.
3. FastAPI validates the request and creates an employee onboarding record.
4. FastAPI starts the LangGraph multi-agent workflow.
5. The Supervisor Agent reads the workflow state.
6. The Supervisor Agent routes the workflow to the Intake Agent.
7. The Intake Agent validates employee information.
8. The Supervisor Agent routes policy-related work to the Policy and Knowledge Agent.
9. The Policy and Knowledge Agent retrieves onboarding context.
10. The Supervisor Agent routes planning work to the Task Planning Agent.
11. The Task Planning Agent generates onboarding tasks.
12. Generated tasks are validated and saved in SQLite.
13. The system generates a welcome email draft.
14. HR reviews and approves or rejects actions.
15. Approved actions are executed through simulated tools.
16. Every important action is logged.
17. The dashboard displays onboarding progress, pending approvals, completed tasks, failed actions, and agent activity.


## 5. Architecture Principles

- Keep the MVP simple and modular.
- Use a Supervisor Agent for coordination.
- Use specialist agents for focused responsibilities.
- Do not build all agents immediately.
- Use human approval before sensitive actions.
- Store important workflow state in the database.
- Log every important agent and user action.
- Simulate enterprise integrations in Version 1.
- Use OpenRouter as the configurable LLM provider layer.
- Avoid hardcoding the application to a single LLM vendor.
- Design the system so real tools and alternative models can be added later.
- Keep agent responsibilities isolated.
- Make routing decisions observable.
- Validate agent outputs before tool execution.


## 6. MVP Architecture Decision

Version 1 prioritizes:

- workflow reliability
- observability
- human approval
- provider flexibility
- supervisor-based routing
- specialist agent separation

The MVP includes only the agents required to prove the multi-agent architecture:

- Supervisor Agent
- Intake Agent
- Policy and Knowledge Agent
- Task Planning Agent

Real email, calendar, HRMS, authentication, manager notifications, and payroll integrations are intentionally deferred to future phases.

OpenRouter will be used as the LLM provider so the system can route requests to configurable models through environment variables.


## 7. System Architecture Diagram

```text
┌──────────────────────┐
│       HR User        │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Streamlit Frontend  │
│  - Employee form     │
│  - Approval screen   │
│  - Dashboard         │
│  - Logs view         │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   FastAPI Backend    │
│  - API routes        │
│  - Request handling  │
│  - Workflow trigger  │
│  - Database access   │
└──────────┬───────────┘
           │
           ▼
┌────────────────────────────────────┐
│ LangGraph Multi-Agent Orchestration │
│ - Workflow state                    │
│ - Routing                           │
│ - Retry handling                    │
│ - Approval pauses                   │
│ - Failure routing                   │
└──────────┬─────────────────────────┘
           │
           ▼
┌──────────────────────────────┐
│       Supervisor Agent       │
│  - Route work                │
│  - Coordinate agents         │
│  - Validate flow             │
│  - Collect outputs           │
│  - Decide approval needs     │
└───────┬──────────┬──────────┘
        │          │
        ▼          ▼
┌──────────────────────────────────────────────┐
│              Specialist Agents              │
│                                              │
│  ┌──────────────────┐  ┌──────────────────┐ │
│  │   Intake Agent   │  │ Policy/Knowledge │ │
│  │ - Validate data  │  │ - Retrieve rules │ │
│  │ - Missing fields │  │ - Templates      │ │
│  └──────────────────┘  └──────────────────┘ │
│                                              │
│  ┌──────────────────────────────┐            │
│  │      Task Planning Agent      │            │
│  │ - Generate checklist          │            │
│  │ - Recommend next actions      │            │
│  └──────────────────────────────┘            │
└───────┬──────────────────────┬──────────────┘
        │                      │
        ▼                      ▼
┌──────────────────────┐   ┌────────────────────────┐
│      Tool Layer      │   │ OpenRouter LLM Layer   │
│ - Checklist tool     │   │ - Model routing        │
│ - Email draft tool   │   │ - Reasoning            │
│ - Approval tool      │   │ - Drafting             │
│ - Task status tool   │   │ - Structured output    │
│ - Audit log tool     │   │ - Configurable models  │
│ - Calendar simulator │   └────────────────────────┘
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────────┐
│          Data Layer          │
│  - SQLite                    │
│  - Employees                 │
│  - Tasks                     │
│  - Approvals                 │
│  - Audit logs                │
│  - Agent runs                │
│  - Workflow state            │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│      Monitoring Layer        │
│  - Python logs               │
│  - SQLite audit logs         │
│  - LangSmith traces          │
│  - Agent activity            │
│  - Routing history           │
└──────────────────────────────┘
```


## 8. Component Responsibilities

| Component                     | Responsibility                                                           |
| ----------------------------- | ------------------------------------------------------------------------ |
| HR User                       | Enters employee details, reviews tasks, approves actions                 |
| Streamlit Frontend            | Provides screens for forms, approvals, dashboard, and logs               |
| FastAPI Backend               | Handles API requests and triggers workflow execution                     |
| LangGraph Orchestration Layer | Controls state, routing, retries, approvals, and failures                |
| Supervisor Agent              | Coordinates workflow and routes work to specialist agents                |
| Intake Agent                  | Validates and structures employee onboarding data                        |
| Policy and Knowledge Agent    | Retrieves onboarding policies, templates, and knowledge                  |
| Task Planning Agent           | Generates onboarding checklist and task recommendations                  |
| OpenRouter LLM Provider Layer | Routes generation requests to configurable LLM models                    |
| Tool Layer                    | Executes controlled system actions                                       |
| SQLite Database               | Stores employees, tasks, approvals, logs, workflow state, and agent runs |
| ChromaDB Memory               | Stores reusable onboarding knowledge and templates                       |
| Monitoring Layer              | Tracks logs, traces, failures, routing history, and agent activity       |


## 9. Agent Communication Model

Agents communicate through structured workflow state.

They do not randomly message each other. The Supervisor Agent controls communication.

### Communication Pattern

```text
Supervisor Agent
↓
Creates structured request
↓
Routes request to specialist agent
↓
Specialist agent executes focused task
↓
Specialist agent returns structured output
↓
Supervisor Agent validates output
↓
Supervisor Agent updates workflow state
```


### Example Agent Request

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


### Example Agent Response

```json
{
  "agent_name": "intake_agent",
  "status": "success",
  "missing_fields": [],
  "validated_employee_profile": {
    "employee_name": "Priya Sharma",
    "role": "Data Analyst",
    "department": "Analytics",
    "joining_date": "2026-06-15"
  }
}
```


## 10. Agent Registry

The system uses an agent registry so the Supervisor Agent knows which agents are available.

### MVP Agent Registry

| Agent Key        | Agent Name                 | Status | Responsibility                |
| ---------------- | -------------------------- | ------ | ----------------------------- |
| supervisor       | Supervisor Agent           | Active | Workflow coordination         |
| intake           | Intake Agent               | Active | Employee data validation      |
| policy_knowledge | Policy and Knowledge Agent | Active | Policy and template retrieval |
| task_planning    | Task Planning Agent        | Active | Checklist generation          |


### Phase 2 Agent Registry

| Agent Key         | Agent Name              | Status   | Responsibility                       |
| ----------------- | ----------------------- | -------- | ------------------------------------ |
| calendar          | Calendar Agent          | Deferred | Calendar scheduling                  |
| manager_follow_up | Manager Follow-up Agent | Deferred | Manager notifications and follow-ups |


## 11. Routing Strategy

The Supervisor Agent owns routing.

Routing is based on workflow state and task intent.

| Condition                                   | Route To                   |
| ------------------------------------------- | -------------------------- |
| Employee data needs validation              | Intake Agent               |
| Employee fields are missing                 | Intake Agent               |
| Onboarding policy context is needed         | Policy and Knowledge Agent |
| Role-specific onboarding template is needed | Policy and Knowledge Agent |
| Checklist needs to be generated             | Task Planning Agent        |
| Generated checklist needs review            | Supervisor Agent           |
| Human approval is required                  | Approval workflow          |
| Tool execution fails                        | Failure Handling Node      |
| Workflow is complete                        | Complete Workflow Node     |


## 12. Detailed Data Flow

### Flow 1: Create New Onboarding Record

1. HR enters employee details in the Streamlit frontend.
2. Frontend sends employee data to FastAPI.
3. FastAPI validates the employee data.
4. FastAPI creates a new employee record in SQLite.
5. FastAPI writes an audit log entry.
6. FastAPI returns the created employee record to the frontend.


### Flow 2: Run Multi-Agent Onboarding Workflow

1. HR clicks “Generate Onboarding Plan.”
2. Frontend sends the employee ID to FastAPI.
3. FastAPI starts the LangGraph workflow.
4. The Supervisor Agent loads employee context.
5. The Supervisor Agent routes to the Intake Agent.
6. The Intake Agent validates required employee data.
7. The Supervisor Agent checks the Intake Agent result.
8. The Supervisor Agent routes to the Policy and Knowledge Agent.
9. The Policy and Knowledge Agent retrieves relevant onboarding context.
10. The Supervisor Agent routes to the Task Planning Agent.
11. The Task Planning Agent generates onboarding tasks.
12. The Supervisor Agent validates the task plan.
13. The Checklist Tool saves validated tasks in SQLite.
14. The Audit Log Tool records agent activity and task generation.
15. Frontend displays the generated checklist to HR.


### Flow 3: Generate Welcome Email Draft

1. HR clicks “Generate Welcome Email.”
2. Frontend sends the employee ID to FastAPI.
3. FastAPI calls the LangGraph workflow.
4. The Supervisor Agent loads employee and onboarding context.
5. The Supervisor Agent routes the draft request to the appropriate generation path.
6. The OpenRouter LLM provider layer generates a welcome email draft.
7. The Email Draft Tool saves the draft.
8. The system marks the email as Awaiting Approval.
9. The Audit Log Tool records the draft generation event.
10. Frontend displays the draft to HR.


### Flow 4: Human Approval

1. HR reviews the generated email or task.
2. HR clicks Approve, Reject, or Request Revision.
3. Frontend sends the approval decision to FastAPI.
4. FastAPI saves the approval record in SQLite.
5. If approved, the workflow moves to execution.
6. If rejected, the workflow marks the item as Rejected or requires revision.
7. The Audit Log Tool records the approval decision.
8. The Supervisor Agent updates workflow state.


### Flow 5: Simulated Tool Execution

1. Approved action is passed to the correct tool.
2. Tool validates its input.
3. Tool performs the simulated action.
4. Tool returns success or failure.
5. If successful, task status is updated to Completed.
6. If failed, task status is updated to Failed.
7. Audit log records the execution result.
8. Dashboard updates the result.


### Flow 6: Monitoring and Logs

1. Every important user action is saved in audit logs.
2. Every important agent step is saved in agent run records.
3. Supervisor routing decisions are saved.
4. Specialist agent outputs are saved.
5. Backend errors are captured through Python logging.
6. LangGraph workflow traces are captured through LangSmith.
7. Dashboard displays recent activity, failed actions, pending approvals, and agent activity.


## 13. LangGraph Multi-Agent Workflow Design

### Workflow Goal

The LangGraph workflow manages the onboarding lifecycle from employee record creation to onboarding progress tracking while ensuring:

- supervisor-based routing
- specialist agent execution
- human approval for sensitive actions
- reliable task execution
- workflow observability
- audit logging
- failure handling
- configurable LLM access through OpenRouter


## 14. Workflow Nodes

### 1. Start Node

Purpose:

- Start onboarding workflow execution.

Input:

- Employee ID

Output:

- Workflow initialization state


### 2. Fetch Employee Data Node

Purpose:

- Retrieve employee information from SQLite.

Input:

- Employee ID

Output:

- Employee profile data

Example fields:

- Name
- Role
- Department
- Joining date
- Email


### 3. Supervisor Routing Node

Purpose:

- Decide which agent should run next.

Input:

- Current workflow state
- Employee profile
- Current workflow status
- Previous agent outputs

Output:

- Next agent route
- Routing reason
- Updated workflow state

Example routes:

- Intake Agent
- Policy and Knowledge Agent
- Task Planning Agent
- Approval Node
- Failure Handling Node
- Complete Workflow Node


### 4. Intake Agent Node

Purpose:

- Validate employee onboarding data.

Input:

- Employee profile data

Output:

- Validated employee profile
- Missing fields
- Validation status

Failure Route:

- Stop workflow and request missing data from HR


### 5. Policy and Knowledge Agent Node

Purpose:

- Retrieve onboarding policies, templates, and knowledge.

Input:

- Employee role
- Department
- Joining date
- Company onboarding context

Output:

- Relevant onboarding policies
- Role-based onboarding template
- Knowledge context for planning

Failure Route:

- Continue with default onboarding template or escalate to manual review


### 6. Task Planning Agent Node

Purpose:

- Generate onboarding tasks using validated employee data and policy context.

Input:

- Validated employee profile
- Policy context
- Role-based onboarding template

Output:

- Generated onboarding checklist
- Approval requirements
- Task priority
- Suggested task ownership

Example tasks:

- Send welcome email
- Schedule orientation
- Request documents
- Assign onboarding buddy
- Share company handbook


### 7. Validate Agent Output Node

Purpose:

- Validate specialist agent outputs before saving or executing them.

Checks:

- Empty outputs
- Duplicate tasks
- Invalid formatting
- Missing critical onboarding steps
- Missing approval flags
- Schema mismatch

Output:

- Validated agent output

Failure Route:

- Retry specialist agent or escalate for manual review


### 8. Save Tasks Node

Purpose:

- Store validated onboarding tasks in SQLite.

Output:

- Task records
- Task IDs


### 9. Generate Welcome Email Node

Purpose:

- Use the OpenRouter LLM provider layer to create an onboarding welcome email draft.

Input:

- Employee profile data
- Generated onboarding tasks
- Company context

Output:

- Email draft


### 10. Approval Node

Purpose:

- Wait for HR approval before sensitive execution.

Possible States:

- Approved
- Rejected
- Revision Requested


### 11. Execute Tool Node

Purpose:

- Execute approved onboarding actions using controlled tools.

Possible Tool Actions:

- Save email draft
- Simulate email sending
- Simulate orientation scheduling
- Update onboarding task status
- Simulate manager notification

Output:

- Success or failure result


### 12. Audit Logging Node

Purpose:

- Record important workflow events.

Logs:

- Supervisor routing
- Specialist agent execution
- Checklist creation
- Approval actions
- Tool execution
- Failures
- Status updates


### 13. Failure Handling Node

Purpose:

- Handle workflow failures safely.

Failure Examples:

- Invalid specialist agent output
- Supervisor routing failure
- OpenRouter request failure
- Database save failure
- Tool execution failure
- Missing employee information

Actions:

- Retry operation
- Log error
- Preserve workflow state
- Escalate for manual review


### 14. Complete Workflow Node

Purpose:

- Mark workflow step as completed.

Output:

- Final onboarding status
- Completion timestamp
- Agent execution summary


## 15. Workflow Routing Logic

### Normal Workflow

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


### Missing Data Route

```text
Intake Agent
→ Missing Required Fields
→ Supervisor Routing
→ Stop Workflow
→ Request HR Update
```


### Validation Failure Route

```text
Task Planning Agent
→ Validate Agent Output
→ Validation Failed
→ Retry Specialist Agent
→ If Retry Fails
→ Manual Review
```


### Approval Rejection Route

```text
Approval
→ Rejected
→ Request Revision
→ Supervisor Routing
→ Relevant Specialist Agent
```


### Tool Failure Route

```text
Execute Tool
→ Failure Handling
→ Retry
→ If Retry Fails
→ Manual Escalation
```


### Critical Failure Route

```text
Critical Error
→ Log Failure
→ Preserve State
→ Stop Workflow
→ Notify HR
```


## 16. Workflow State Design

### Workflow State Purpose

The workflow state stores all important onboarding information required by the LangGraph multi-agent workflow during execution.

The state allows:

- workflow continuity
- supervisor routing
- agent coordination
- task tracking
- approval handling
- retry handling
- audit logging
- failure recovery


## State Fields

| Field                     | Purpose                                  |
| ------------------------- | ---------------------------------------- |
| employee_id               | Unique employee identifier               |
| employee_name             | Employee full name                       |
| employee_email            | Employee email                           |
| role                      | Employee role                            |
| department                | Employee department                      |
| joining_date              | Employee joining date                    |
| onboarding_tasks          | Generated onboarding checklist           |
| email_draft               | Generated welcome email                  |
| approval_status           | Current approval state                   |
| task_status               | Current workflow task state              |
| current_node              | Current LangGraph node                   |
| current_agent             | Agent currently executing                |
| next_agent                | Agent selected by Supervisor Agent       |
| supervisor_routing_reason | Reason for routing decision              |
| agent_execution_history   | History of specialist agent calls        |
| agent_outputs             | Structured outputs returned by agents    |
| retry_count               | Number of retries attempted              |
| failure_reason            | Failure details if workflow fails        |
| audit_events              | Workflow event history                   |
| tool_execution_result     | Tool execution response                  |
| workflow_status           | Overall workflow status                  |
| llm_provider              | Selected LLM provider                    |
| llm_model                 | Selected model routed through OpenRouter |


## Example Workflow State

```json
{
  "employee_id": "EMP_001",
  "employee_name": "Priya Sharma",
  "employee_email": "priya@company.com",
  "role": "Data Analyst",
  "department": "Analytics",
  "joining_date": "2026-06-15",
  "current_node": "Supervisor Routing Node",
  "current_agent": "supervisor",
  "next_agent": "task_planning",
  "supervisor_routing_reason": "Employee data is valid and policy context is available. Task planning can begin.",
  "onboarding_tasks": [
    "Send welcome email",
    "Schedule orientation",
    "Collect ID proof"
  ],
  "approval_status": "Awaiting Approval",
  "task_status": "In Progress",
  "retry_count": 0,
  "workflow_status": "Running",
  "llm_provider": "OpenRouter",
  "llm_model": "openai/gpt-4.1"
}
```


## State Transition Principles

- Every node can read workflow state.
- The Supervisor Agent controls routing.
- Specialist agents only modify fields relevant to their responsibility.
- Important state changes must be logged.
- Failed workflows should preserve state for debugging and retries.
- Approval state must always be persisted in SQLite.
- Model provider and model configuration should remain explicit and observable.
- Agent name, agent role, and routing reason should be captured for observability.


## 17. Guardrails and Failure Protection

### Guardrail Philosophy

The platform is designed as a controlled and observable multi-agent workflow system rather than a fully autonomous agent.

The architecture intentionally prioritizes:

- workflow safety
- execution reliability
- human supervision
- deterministic routing
- auditability
- operational traceability

The workflow should never silently continue after critical failures.


## Core Guardrails

### 1. Human Approval Guardrail

Sensitive onboarding actions require explicit HR approval before execution.

Examples:

- sending official onboarding emails
- requesting sensitive employee documents
- marking onboarding as completed
- notifying managers
- creating access-related tasks

Purpose:

- prevent unsafe automation
- maintain human accountability
- reduce operational risk


### 2. Supervisor Routing Guardrail

The Supervisor Agent must route work only to registered agents.

The Supervisor Agent must not:

- call unknown agents
- skip required validation steps
- bypass human approval
- execute sensitive actions directly
- continue after critical state corruption


### 3. Specialist Responsibility Guardrail

Each specialist agent must stay within its assigned responsibility.

Examples:

- Intake Agent validates data but does not generate final task plans.
- Policy and Knowledge Agent retrieves context but does not approve actions.
- Task Planning Agent generates checklist items but does not execute tools.

This keeps the system predictable and easier to debug.


### 4. Structured Output Validation

AI-generated outputs must be validated before execution or persistence.

Validation includes:

- empty output detection
- malformed structure detection
- duplicate task detection
- mandatory onboarding step validation
- response schema validation
- missing approval flag detection

Invalid outputs should:

- fail safely
- trigger retries when appropriate
- escalate if retries fail


### 5. Controlled Tool Execution

The workflow controls all tool execution.

The configured model must never:

- directly modify database records
- bypass approval workflows
- execute unrestricted actions
- invoke arbitrary system functions

All tools must:

- validate input
- return structured responses
- log execution results
- expose failure details


### 6. Workflow State Persistence

Critical workflow state must remain persisted in SQLite.

The workflow should preserve:

- onboarding progress
- approval states
- retry history
- workflow failures
- execution metadata
- routing decisions
- agent outputs
- audit history

This prevents workflow loss during:

- backend crashes
- process restarts
- temporary infrastructure failures


### 7. Retry Protection

Retries should remain controlled and finite.

The workflow must avoid:

- infinite retry loops
- uncontrolled recursive execution
- silent retry failures


## Retry Limits

| Failure Type                               | Max Retries |
| ------------------------------------------ | ----------- |
| Specialist agent output validation failure | 2           |
| Supervisor routing failure                 | 1           |
| OpenRouter request failure                 | 2           |
| Tool execution failure                     | 2           |
| Database write failure                     | 1           |
| Workflow validation failure                | 2           |

After retry exhaustion:

- workflow execution should stop safely
- failure context should be preserved
- manual review should be triggered


### 8. Failure Escalation

Critical workflow failures must trigger escalation paths.

Escalation conditions include:

- repeated retry failures
- malformed workflow state
- invalid supervisor routing
- persistent provider failures
- tool execution instability
- approval deadlocks

Escalation actions:

- stop workflow execution
- preserve workflow state
- write audit logs
- expose failure details to HR
- require manual intervention


### 9. Auditability Guardrail

All important workflow actions must remain observable.

Observable events include:

- onboarding creation
- workflow transitions
- supervisor routing decisions
- specialist agent execution
- approvals
- retries
- failures
- tool execution
- model provider failures
- workflow completion
- destructive action requests
- destructive action approvals or rejections
- exception details
- retry attempts and retry exhaustion
- human escalation events

The system should maintain:

- Python backend logs
- SQLite audit logs
- LangSmith traces
- workflow execution metadata
- agent execution metadata


### 10. Secret Management Guardrail

Sensitive credentials must never be hardcoded.

Protected credentials include:

- OpenRouter API keys
- LangSmith API keys
- database credentials
- deployment secrets

Secrets must:

- remain inside environment variables
- never appear in logs
- never appear in audit records
- never be committed to Git


### 11. Provider Isolation Guardrail

The architecture intentionally avoids tight coupling to a single model provider.

The OpenRouter provider layer exists to:

- support configurable model routing
- improve provider flexibility
- simplify future provider replacement
- isolate workflow logic from provider-specific implementation

Future providers may include:

- direct OpenAI
- Azure OpenAI
- Anthropic
- local models
- enterprise-hosted models


### 12. Observability Guardrail

Workflow execution must remain transparent and traceable.

The system should expose:

- workflow status
- node execution state
- current agent
- next agent
- supervisor routing reason
- retry counts
- approval state
- failure reasons
- model provider metadata
- configured model metadata

Observability is considered mandatory infrastructure.


## Failure Handling Lifecycle

```text
Failure Detected
↓
Capture Failure Context
↓
Write Audit Log
↓
Update Workflow State
↓
Route To Failure Handling Node
↓
Retry If Recoverable
↓
Escalate If Retry Limit Reached
↓
Require Manual Review
```


## Guardrail Design Summary

The guardrail architecture is designed to ensure:

- safe AI-assisted onboarding execution
- controlled workflow automation
- reliable workflow recovery
- observable execution behavior
- human-supervised decision making
- deterministic supervisor routing
- specialist agent isolation

The system intentionally favors:

- reliability
- auditability
- operational safety
- provider flexibility
- workflow transparency

over:

- unrestricted autonomy
- uncontrolled execution
- opaque decision making
- unnecessary agent complexity


## 18. Database Architecture

### Database Goal

The database stores structured onboarding workflow data required for:

- workflow continuity
- approvals
- monitoring
- audit logging
- retries
- task tracking
- debugging
- agent observability

SQLite will be used for the MVP version.


## Database Tables

## 1. employees

Purpose:

Store employee onboarding records.

| Field          | Type | Description                |
| -------------- | ---- | -------------------------- |
| employee_id    | TEXT | Unique employee identifier |
| employee_name  | TEXT | Full employee name         |
| employee_email | TEXT | Employee email             |
| role           | TEXT | Employee role              |
| department     | TEXT | Employee department        |
| joining_date   | TEXT | Employee joining date      |
| created_at     | TEXT | Record creation timestamp  |


## 2. onboarding_tasks

Purpose:

Store onboarding tasks generated by the Task Planning Agent.

| Field              | Type    | Description                      |
| ------------------ | ------- | -------------------------------- |
| task_id            | TEXT    | Unique task identifier           |
| employee_id        | TEXT    | Related employee                 |
| task_name          | TEXT    | Task description                 |
| task_status        | TEXT    | Pending, Completed, Failed, etc. |
| approval_required  | BOOLEAN | Whether HR approval is required  |
| generated_by_agent | TEXT    | Agent that generated the task    |
| created_at         | TEXT    | Task creation timestamp          |


## 3. approvals

Purpose:

Store HR approval decisions.

| Field           | Type | Description                            |
| --------------- | ---- | -------------------------------------- |
| approval_id     | TEXT | Unique approval identifier             |
| employee_id     | TEXT | Related employee                       |
| action_type     | TEXT | Action awaiting approval               |
| approval_status | TEXT | Approved, Rejected, Revision Requested |
| reviewed_by     | TEXT | HR reviewer                            |
| reviewed_at     | TEXT | Review timestamp                       |


## 4. audit_logs

Purpose:

Store important system, user, workflow, and agent events.

| Field         | Type | Description                      |
| ------------- | ---- | -------------------------------- |
| log_id        | TEXT | Unique log identifier            |
| employee_id   | TEXT | Related employee                 |
| event_type    | TEXT | Event category                   |
| event_message | TEXT | Human-readable event description |
| agent_name    | TEXT | Agent involved in the event      |
| timestamp     | TEXT | Event timestamp                  |

Example Events:

- Employee created
- Supervisor routed to Intake Agent
- Intake Agent validation completed
- Policy and Knowledge Agent retrieved template
- Task Planning Agent generated checklist
- Email approved
- Tool execution failed
- Workflow completed
- OpenRouter request failed
- Model output validation failed


## 5. agent_runs

Purpose:

Store LangGraph multi-agent workflow execution details.

| Field           | Type    | Description                                     |
| --------------- | ------- | ----------------------------------------------- |
| run_id          | TEXT    | Unique workflow run ID                          |
| employee_id     | TEXT    | Related employee                                |
| current_node    | TEXT    | Current workflow node                           |
| agent_name      | TEXT    | Agent that executed                             |
| agent_role      | TEXT    | Supervisor, Intake, Policy, Task Planning, etc. |
| input_summary   | TEXT    | Summary of agent input                          |
| output_summary  | TEXT    | Summary of agent output                         |
| routing_reason  | TEXT    | Supervisor reason for selecting agent           |
| workflow_status | TEXT    | Running, Failed, Completed                      |
| retry_count     | INTEGER | Retry attempts                                  |
| llm_provider    | TEXT    | LLM provider used for the run                   |
| llm_model       | TEXT    | Model used through OpenRouter                   |
| started_at      | TEXT    | Workflow start timestamp                        |
| completed_at    | TEXT    | Workflow completion timestamp                   |


## Database Relationships

```text
employees
↓
onboarding_tasks
↓
approvals
↓
audit_logs
↓
agent_runs
```

Each employee can have:

- multiple onboarding tasks
- multiple approvals
- multiple audit logs
- multiple workflow runs
- multiple agent run records


## Database Design Principles

- Store workflow state persistently.
- Never rely entirely on model memory.
- Log important workflow events.
- Preserve failure information for debugging.
- Support retries and workflow recovery.
- Keep schema simple for MVP scalability.
- Preserve provider and model metadata for observability.
- Preserve agent name, agent role, routing reason, and execution result.


## 19. Tool Architecture

### Tool Architecture Goal

The tool layer provides controlled functions that allow the LangGraph workflow to perform specific onboarding actions safely and consistently.

Tools prevent LLMs and agents from directly modifying system data.

Tools help maintain:

- reliability
- observability
- safety
- modularity
- testability


## Tool Design Principle

Agents can suggest or generate outputs, but tools perform actual system actions.

Example:

Agent output:

- “Create onboarding checklist for Data Analyst.”

Tool action:

- Save validated checklist tasks into SQLite.


## Planned MVP Tools

### 1. Checklist Tool

Purpose:

- Save Task Planning Agent-generated onboarding tasks into the database.

Input:

- Employee ID
- List of onboarding tasks
- Agent name
- Approval requirements

Output:

- Saved task records
- Task IDs
- Success or failure status


### 2. Email Draft Tool

Purpose:

- Save AI-generated welcome email drafts.

Input:

- Employee ID
- Email subject
- Email body
- Agent or workflow source

Output:

- Saved email draft record
- Approval status set to Awaiting Approval


### 3. Approval Tool

Purpose:

- Store HR approval or rejection decisions.

Input:

- Employee ID
- Action type
- Approval decision
- Reviewer name

Output:

- Approval record
- Updated task or email status


### 4. Task Status Tool

Purpose:

- Update onboarding task status.

Input:

- Task ID
- New status

Output:

- Updated task record


### 5. Audit Log Tool

Purpose:

- Record important system, user, workflow, and agent events.

Input:

- Employee ID
- Event type
- Event message
- Agent name
- Routing metadata when available

Output:

- Audit log record


### 6. Calendar Simulation Tool

Purpose:

- Simulate scheduling orientation.

Input:

- Employee ID
- Orientation title
- Scheduled date
- Attendees

Output:

- Simulated calendar event
- Success or failure status


### 7. Notification Simulation Tool

Purpose:

- Simulate notifying a hiring manager or HR user.

Input:

- Employee ID
- Recipient type
- Message

Output:

- Notification record
- Success or failure status


## Tool Execution Flow

1. Supervisor Agent identifies that a tool action is needed.
2. Required input data is validated.
3. Human approval is checked if required.
4. Tool executes the controlled action.
5. Tool returns success or failure.
6. Result is stored in workflow state.
7. Audit Log Tool records the action.
8. Dashboard displays updated status.


## Tool Failure Handling

If a tool fails, the system should:

- capture the error message
- update task status to Failed
- write an audit log
- increase retry count
- route workflow to Failure Handling Node
- preserve agent and tool metadata


## Tool Design Principles

- Each tool should do one specific job.
- Tools should validate input before execution.
- Tools should return structured responses.
- Tools should log success and failure events.
- Tools should never expose sensitive data unnecessarily.
- Tools should be easy to replace with real integrations later.
- Tools should record the agent or workflow source that triggered them.


## 20. API Architecture

### API Architecture Goal

The API layer allows the Streamlit frontend to communicate with the FastAPI backend.

The backend exposes controlled endpoints for:

- creating employee onboarding records
- triggering multi-agent onboarding workflows
- generating onboarding checklists
- generating welcome email drafts
- approving or rejecting AI-generated actions
- updating task status
- retrieving dashboard data
- retrieving audit logs
- retrieving agent execution history


## API Design Principles

- APIs should have clear request and response formats.
- APIs should validate input before processing.
- APIs should not expose internal LangGraph implementation details unnecessarily.
- APIs should return meaningful error messages.
- APIs should trigger audit logging for important actions.
- APIs should support future replacement of the frontend.
- APIs should expose agent activity in a safe and readable way.


## Planned MVP API Endpoints

### 1. Create Employee

Endpoint:

```http
POST /employees
```

Purpose:

- Create a new employee onboarding record.


### 2. Generate Onboarding Plan

Endpoint:

```http
POST /employees/{employee_id}/generate-onboarding-plan
```

Purpose:

- Trigger the Supervisor Agent and specialist agents to generate an onboarding plan.


### 3. Generate Checklist

Endpoint:

```http
POST /employees/{employee_id}/generate-checklist
```

Purpose:

- Trigger the multi-agent workflow to generate onboarding tasks.


### 4. Generate Welcome Email Draft

Endpoint:

```http
POST /employees/{employee_id}/generate-email-draft
```

Purpose:

- Generate a welcome email draft for HR review.


### 5. Submit Approval Decision

Endpoint:

```http
POST /approvals
```

Purpose:

- Submit HR approval, rejection, or revision request.


### 6. Update Task Status

Endpoint:

```http
PATCH /tasks/{task_id}/status
```

Purpose:

- Update onboarding task status.


### 7. Get Employee Onboarding Status

Endpoint:

```http
GET /employees/{employee_id}/status
```

Purpose:

- Retrieve employee onboarding progress.


### 8. Get Dashboard Summary

Endpoint:

```http
GET /dashboard
```

Purpose:

- Retrieve overall onboarding dashboard metrics.


### 9. Get Audit Logs

Endpoint:

```http
GET /audit-logs
```

Purpose:

- Retrieve recent system and agent activity.


### 10. Get Agent Runs

Endpoint:

```http
GET /agent-runs
```

Purpose:

- Retrieve recent agent execution history.


### 11. Get Employee Agent Runs

Endpoint:

```http
GET /employees/{employee_id}/agent-runs
```

Purpose:

- Retrieve agent activity for a specific employee onboarding workflow.


## API Error Handling

APIs should return clear error responses.

Example:

```json
{
  "error": true,
  "error_type": "VALIDATION_ERROR",
  "message": "Employee email is required."
}
```

Common error types:

- VALIDATION_ERROR
- NOT_FOUND
- WORKFLOW_ERROR
- ROUTING_ERROR
- AGENT_EXECUTION_ERROR
- TOOL_EXECUTION_ERROR
- DATABASE_ERROR
- LLM_PROVIDER_ERROR


## API Security Notes

For MVP:

- Authentication can be deferred.
- Sensitive actions must still require approval.
- Input validation is mandatory.
- No API should expose unnecessary employee data.
- OpenRouter API keys must be stored only in environment variables.
- Agent execution logs should not expose raw secrets or sensitive credential values.

For future versions:

- Add authentication.
- Add role-based access control.
- Add rate limiting.
- Add audit retention policies.


## 21. Architecture Tradeoffs

### Why Streamlit Is Used For MVP

Streamlit is selected because it allows fast development of forms, dashboards, approval screens, and logs views.

Tradeoff:

- Streamlit is not ideal for complex enterprise-grade frontend applications.

Future Option:

- Replace Streamlit with React or Next.js when the product requires advanced UI, authentication, and role-based workflows.


### Why SQLite Is Used For MVP

SQLite is selected because it is simple, lightweight, and easy to set up for local development.

Tradeoff:

- SQLite is not ideal for high-concurrency enterprise workloads.

Future Option:

- Replace SQLite with PostgreSQL when multiple users, production deployment, and stronger data management are required.


### Why Tools Are Simulated In Version 1

Email, calendar, HRMS, and notification tools are simulated to reduce implementation complexity.

Tradeoff:

- The MVP will not send real emails or create real calendar events.

Future Option:

- Replace simulated tools with Gmail, Outlook, Google Calendar, Slack, Microsoft Teams, or HRMS integrations.


### Why Human Approval Is Required

Human approval is used to prevent unsafe or incorrect automated actions.

Tradeoff:

- Approval steps reduce full automation speed.

Future Option:

- Low-risk actions can become auto-approved in future versions after enough system reliability is measured.


### Why LangGraph Is Used

LangGraph is selected because the workflow requires state, routing, retries, approval handling, and failure handling.

Tradeoff:

- LangGraph requires more upfront design than a simple LLM chain.

Future Option:

- Keep LangGraph as the orchestration layer and add more specialized agents only when the workflow justifies them.


### Why OpenRouter Is Used

OpenRouter is selected to provide configurable model routing and reduce direct dependency on a single LLM vendor.

Tradeoff:

- Model behavior, latency, pricing, and output quality may vary depending on the configured model.

Future Option:

- Add a provider abstraction layer that supports OpenRouter, direct OpenAI, Azure OpenAI, Anthropic, or local models behind the same internal interface.


### Why Supervisor-Based Multi-Agent Architecture Is Used

A supervisor-based architecture is selected because onboarding contains different types of work:

- data validation
- policy lookup
- task planning
- approval handling
- tool execution
- monitoring

Putting everything into one agent would make the system harder to debug and scale.

Tradeoff:

- Multi-agent architecture adds routing and state-management complexity.

Future Option:

- Add more agents only after the MVP supervisor and core specialist agents are stable.


## 22. Architecture Review Summary

The Onboarding Buddy architecture is designed as a modular, stateful, observable, supervisor-based multi-agent workflow system.

The architecture supports:

- HR-driven onboarding workflows
- Supervisor Agent coordination
- specialist agent execution
- AI-generated onboarding plans
- configurable LLM access through OpenRouter
- human approval checkpoints
- controlled tool execution
- persistent workflow state
- audit logging
- failure handling
- dashboard visibility
- agent observability

The MVP intentionally avoids complex enterprise integrations in order to prioritize:

- reliable workflow execution
- clear system behavior
- provider flexibility
- simple deployment
- easier debugging
- faster portfolio delivery
- believable multi-agent implementation

This architecture is suitable for a portfolio-grade AI engineering project and can be extended into a more enterprise-ready system in future phases.
