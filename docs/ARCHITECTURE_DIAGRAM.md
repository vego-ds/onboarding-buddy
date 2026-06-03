# Architecture Diagram

## Component View

```mermaid
flowchart TD
    HR["HR User"] --> UI["Streamlit Frontend"]
    UI --> API["FastAPI Backend"]
    API --> Employees["Employee Routes"]
    API --> Tasks["Task Routes"]
    API --> Approvals["Approval Routes"]
    API --> Runs["Workflow Run Routes"]
    API --> Service["Workflow Service"]
    Service --> Graph["LangGraph StateGraph"]
    Graph --> Supervisor["Supervisor Agent"]
    Supervisor --> Intake["Intake Agent"]
    Intake --> Supervisor
    Supervisor --> Planner["Task Planning Agent"]
    Planner --> Supervisor
    Planner --> LLM["OpenRouter LLM"]
    Supervisor --> LLM
    Employees --> Repos["Repository Layer"]
    Tasks --> Repos
    Approvals --> Repos
    Runs --> Repos
    Service --> Repos
    Repos --> DB[("PostgreSQL")]
```

## Workflow Sequence

```mermaid
sequenceDiagram
    participant HR as HR User
    participant UI as Streamlit
    participant API as FastAPI
    participant WF as LangGraph Workflow
    participant S as Supervisor
    participant I as Intake Agent
    participant T as Task Planning Agent
    participant DB as PostgreSQL

    HR->>UI: Create employee
    UI->>API: POST /employees
    API->>DB: Save employee
    HR->>UI: Generate plan
    UI->>API: POST /employees/{id}/generate-onboarding-plan
    API->>DB: Create workflow run
    API->>WF: Start workflow with workflow_run_id
    WF->>S: Route next step
    S->>I: Validate employee profile
    I->>S: Validation result
    S->>T: Generate onboarding tasks
    T->>DB: Save tasks, approvals, dependencies
    T->>S: Task output
    S->>WF: Complete workflow
    API->>DB: Save agent runs and complete workflow run
    API->>DB: Mark employee PLAN_READY
    API->>UI: Return task plan and workflow_run_id
```

## Operations Flow

```mermaid
flowchart TD
    Ops["Operations Workspace"] --> Queue["Approval Queue"]
    Ops --> Status["Task Status Controls"]
    Ops --> Timeline["Employee Timeline"]
    Ops --> RunPanel["Workflow Run Panel"]
    Queue --> ApprovalAPI["PATCH /approvals/{approval_id}"]
    Status --> TaskAPI["PATCH /tasks/{task_id}/status"]
    TaskAPI --> Rules["Dependency and Approval Enforcement"]
    ApprovalAPI --> Unlock["Approval Unlock Logic"]
    Rules --> Audit["Timeline Events"]
    Unlock --> Audit
```
