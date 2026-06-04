# Onboarding Buddy Project Structure

## 1. Project Goal

The project structure is designed to support:

* supervisor-based multi-agent orchestration
* modular development
* maintainability
* workflow scalability
* safe AI orchestration
* observability
* provider flexibility
* future enterprise integrations

The architecture separates frontend, backend, orchestration, specialist agents, tools, monitoring, persistence layers, and provider abstraction layers into isolated modules to improve engineering clarity and long-term scalability.

The repository structure mirrors the multi-agent architecture directly.

---

# 2. Repository Structure

```text
onboarding-buddy/
│
├── frontend/
│   ├── app.py
│   ├── pages/
│   │   ├── dashboard.py
│   │   ├── onboarding_form.py
│   │   ├── approvals.py
│   │   ├── workflow_logs.py
│   │   └── agent_activity.py
│   │
│   ├── components/
│   │   ├── employee_form.py
│   │   ├── task_table.py
│   │   ├── approval_card.py
│   │   ├── workflow_status.py
│   │   └── agent_trace_viewer.py
│   │
│   └── utils/
│       ├── api_client.py
│       └── formatting.py
│
├── backend/
│   ├── main.py
│   │
│   ├── routes/
│   │   ├── employees.py
│   │   ├── tasks.py
│   │   ├── approvals.py
│   │   ├── dashboard.py
│   │   ├── audit_logs.py
│   │   └── agent_runs.py
│   │
│   ├── services/
│   │   ├── onboarding_service.py
│   │   ├── workflow_service.py
│   │   ├── approval_service.py
│   │   └── monitoring_service.py
│   │
│   ├── middleware/
│   │   ├── request_logging.py
│   │   └── error_handler.py
│   │
│   └── config/
│       ├── settings.py
│       └── environment.py
│
├── agents/
│   │
│   ├── supervisor/
│   │   ├── agent.py
│   │   ├── routing.py
│   │   ├── state_manager.py
│   │   ├── validation.py
│   │   └── prompts.py
│   │
│   ├── intake/
│   │   ├── agent.py
│   │   ├── validation.py
│   │   ├── transformers.py
│   │   └── prompts.py
│   │
│   ├── policy/
│   │   ├── agent.py
│   │   ├── retrieval.py
│   │   ├── templates.py
│   │   └── prompts.py
│   │
│   ├── task_planning/
│   │   ├── agent.py
│   │   ├── checklist_generator.py
│   │   ├── task_validator.py
│   │   └── prompts.py
│   │
│   ├── knowledge/
│   │   ├── faq_retriever.py
│   │   ├── onboarding_examples.py
│   │   └── embeddings_search.py
│   │
│   ├── calendar/
│   │   ├── agent.py
│   │   └── scheduler.py
│   │
│   ├── manager/
│   │   ├── agent.py
│   │   └── followup.py
│   │
│   ├── shared/
│   │   ├── base_agent.py
│   │   ├── agent_registry.py
│   │   ├── workflow_state.py
│   │   ├── output_parser.py
│   │   ├── retry_handler.py
│   │   └── constants.py
│   │
│   ├── workflow/
│   │   ├── graph.py
│   │   ├── nodes.py
│   │   ├── edges.py
│   │   ├── conditional_routes.py
│   │   ├── approval_nodes.py
│   │   ├── failure_nodes.py
│   │   └── workflow_builder.py
│   │
│   └── prompts/
│       ├── supervisor_prompts.py
│       ├── intake_prompts.py
│       ├── policy_prompts.py
│       ├── planning_prompts.py
│       └── shared_prompts.py
│
├── llm/
│   ├── openrouter_client.py
│   ├── provider_manager.py
│   ├── model_router.py
│   ├── model_config.py
│   ├── structured_outputs.py
│   ├── prompt_templates.py
│   └── response_validator.py
│
├── tools/
│   ├── checklist_tool.py
│   ├── email_tool.py
│   ├── approval_tool.py
│   ├── task_tool.py
│   ├── logging_tool.py
│   ├── calendar_tool.py
│   ├── notification_tool.py
│   └── tool_registry.py
│
├── database/
│   ├── models/
│   │   ├── employee.py
│   │   ├── onboarding_task.py
│   │   ├── approval.py
│   │   ├── audit_log.py
│   │   └── agent_run.py
│   │
│   ├── repositories/
│   │   ├── employee_repository.py
│   │   ├── task_repository.py
│   │   ├── approval_repository.py
│   │   ├── audit_repository.py
│   │   └── agent_run_repository.py
│   │
│   ├── migrations/
│   │
│   ├── schema.sql
│   └── db.py
│
├── memory/
│   ├── chroma_client.py
│   ├── embeddings.py
│   ├── policy_memory.py
│   ├── onboarding_templates.py
│   └── faq_memory.py
│
├── monitoring/
│   ├── logger.py
│   ├── audit.py
│   ├── langsmith.py
│   ├── workflow_tracing.py
│   ├── routing_monitor.py
│   ├── failure_monitor.py
│   └── metrics.py
│
├── schemas/
│   ├── employee.py
│   ├── task.py
│   ├── approval.py
│   ├── agent.py
│   ├── workflow.py
│   └── api_response.py
│
├── tests/
│   ├── test_supervisor/
│   ├── test_intake/
│   ├── test_policy/
│   ├── test_task_planning/
│   ├── test_workflow/
│   ├── test_tools/
│   ├── test_routes/
│   ├── test_database/
│   └── test_monitoring/
│
├── docs/
│   ├── PRD.md
│   ├── SYSTEM_ARCHITECTURE.md
│   ├── AGENT_WORKFLOW_MAP.md
│   ├── PROJECT_STRUCTURE.md
│   ├── DATABASE_SCHEMA.md
│   ├── LANGGRAPH_WORKFLOW.md
│   └── API_DESIGN.md
│
├── logs/
│   ├── backend.log
│   ├── workflow.log
│   ├── agent.log
│   └── errors.log
│
├── scripts/
│   ├── seed_database.py
│   ├── run_workflow.py
│   └── generate_mock_data.py
│
├── .env
├── .gitignore
├── requirements.txt
├── README.md
├── docker-compose.yml
└── pyproject.toml
```

---

# 3. Folder Responsibilities

| Folder     | Responsibility                                       |
| ---------- | ---------------------------------------------------- |
| frontend   | Streamlit user interface                             |
| backend    | FastAPI backend APIs                                 |
| agents     | Multi-agent orchestration system                     |
| llm        | OpenRouter provider abstraction and model management |
| tools      | Controlled tool execution layer                      |
| database   | Database models and persistence                      |
| memory     | Vector memory and onboarding knowledge               |
| monitoring | Logs, tracing, and observability                     |
| schemas    | Pydantic request and response schemas                |
| tests      | Automated testing                                    |
| docs       | Project documentation                                |
| logs       | Runtime log files                                    |
| scripts    | Utility scripts and local tooling                    |

---

# 4. Frontend Layer

The frontend layer is built using Streamlit.

Responsibilities:

* employee onboarding form
* onboarding dashboard
* approval screens
* task tracking screens
* workflow visibility
* audit log visibility
* agent activity visibility
* routing trace visibility

The frontend should:

* remain lightweight
* avoid direct database access
* communicate only through backend APIs
* expose workflow execution clearly

---

# 5. Backend Layer

The backend layer is built using FastAPI.

Responsibilities:

* API route management
* workflow triggering
* request validation
* onboarding coordination
* database interaction
* response formatting
* workflow execution startup
* approval management

The backend acts as the communication layer between the frontend and the LangGraph multi-agent orchestration system.

---

# 6. Multi-Agent Layer

The agents folder contains the core multi-agent orchestration system.

The architecture uses:

```text id="8o9l8w"
1 Supervisor Agent
+
Multiple Specialist Agents
```

---

## Supervisor Agent

The Supervisor Agent is responsible for:

* workflow coordination
* routing decisions
* workflow state management
* retry handling
* output validation
* failure routing
* approval routing
* final workflow summaries

Important files:

| File             | Purpose                 |
| ---------------- | ----------------------- |
| agent.py         | Supervisor Agent logic  |
| routing.py       | Agent routing decisions |
| state_manager.py | Workflow state updates  |
| validation.py    | Workflow validation     |
| prompts.py       | Supervisor prompts      |

The Supervisor Agent acts as the orchestration brain.

---

## Intake Agent

The Intake Agent validates employee onboarding information.

Responsibilities:

* missing field detection
* employee profile validation
* onboarding input normalization
* validation error handling

---

## Policy Agent

The Policy Agent retrieves onboarding policies and templates.

Responsibilities:

* onboarding template retrieval
* onboarding rule retrieval
* policy context generation
* onboarding memory search

---

## Task Planning Agent

The Task Planning Agent generates onboarding checklists.

Responsibilities:

* onboarding task generation
* checklist structuring
* approval requirement tagging
* task validation

---

## Deferred Agents

These agents are intentionally deferred beyond the current workflow graph.

### Calendar Agent

Responsibilities:

* onboarding scheduling
* orientation planning
* meeting coordination

### Manager Agent

Responsibilities:

* manager reminders
* onboarding follow-ups
* escalation notifications

---

## Shared Agent Infrastructure

The shared folder contains reusable orchestration infrastructure.

Responsibilities:

* workflow state definitions
* retry handling
* output parsing
* agent registry
* base agent logic
* constants

The shared infrastructure prevents duplicated orchestration logic.

---

## Workflow Layer

The workflow folder contains LangGraph orchestration logic.

Responsibilities:

* graph construction
* node registration
* edge routing
* conditional branching
* approval flow handling
* failure handling

Important files:

| File                  | Purpose                |
| --------------------- | ---------------------- |
| graph.py              | Main LangGraph graph   |
| nodes.py              | Workflow nodes         |
| edges.py              | Workflow edges         |
| conditional_routes.py | Dynamic routing        |
| approval_nodes.py     | Human approval nodes   |
| failure_nodes.py      | Failure recovery nodes |

The workflow layer controls execution order and routing behavior.

---

# 7. LLM Provider Layer

The llm folder contains provider abstraction logic and model orchestration infrastructure.

Responsibilities:

* OpenRouter integration
* configurable model routing
* provider isolation
* centralized model configuration
* structured output validation
* prompt management
* request abstraction
* response validation
* future provider extensibility

Important files:

| File                  | Purpose                        |
| --------------------- | ------------------------------ |
| openrouter_client.py  | OpenRouter API communication   |
| provider_manager.py   | Provider abstraction layer     |
| model_router.py       | Model selection logic          |
| structured_outputs.py | Structured response validation |
| response_validator.py | LLM output validation          |

The provider layer isolates workflow orchestration from provider-specific implementation details.

The architecture intentionally avoids tightly coupling workflow execution to:

* OpenAI-specific SDK logic
* provider-specific response formats
* provider-specific orchestration assumptions

---

# 8. Tool Layer

The tools folder contains isolated executable tools used by the LangGraph workflow.

Responsibilities:

* checklist persistence
* email draft handling
* approval storage
* task status updates
* logging
* simulated integrations
* notification simulation

Each tool should:

* perform one specific action
* validate input
* return structured output
* remain isolated from model reasoning
* log execution metadata

The configured model should never directly modify the database.

---

# 9. Database Layer

The database layer manages structured persistence.

Responsibilities:

* employee records
* onboarding tasks
* approvals
* audit logs
* workflow execution history
* agent execution history
* routing metadata
* provider metadata persistence
* retry tracking

PostgreSQL is used for the runtime database.

---

# 10. Memory Layer

The future memory layer will support vector memory functionality.

Potential use cases:

* onboarding templates
* company FAQs
* role-specific onboarding examples
* reusable onboarding flows
* reusable email examples
* onboarding policies

ChromaDB is planned as the MVP vector database.

---

# 11. Monitoring Layer

The monitoring layer handles observability.

Responsibilities:

* backend logging
* workflow tracing
* audit event tracking
* provider request visibility
* retry visibility
* routing visibility
* failure recording
* debugging support
* agent activity tracking

Monitoring components:

| Component          | Purpose                       |
| ------------------ | ----------------------------- |
| logger.py          | Python backend logging        |
| audit.py           | Audit event recording         |
| langsmith.py       | LangGraph tracing             |
| routing_monitor.py | Supervisor routing visibility |
| failure_monitor.py | Failure tracking              |
| metrics.py         | Workflow metrics              |

Observability is considered a first-class engineering requirement.

The monitoring layer should expose:

* provider request failures
* configured model metadata
* workflow retry activity
* workflow transition visibility
* execution failure context
* routing decisions
* specialist agent execution history

---

# 12. Schema Layer

The schemas folder contains Pydantic schemas.

Responsibilities:

* request validation
* response validation
* API typing
* structured payload formatting
* workflow state typing
* agent response typing

Example schemas:

* EmployeeCreateRequest
* ApprovalRequest
* TaskResponse
* AgentRunResponse
* WorkflowStateResponse

---

# 13. Testing Layer

The tests folder contains automated tests.

Testing areas:

* Supervisor Agent routing
* specialist agent execution
* workflow logic
* API routes
* tool execution
* database operations
* provider integration
* failure handling
* retry routing
* structured output validation

Even basic automated testing significantly improves engineering reliability and maintainability.

---

# 14. Documentation Layer

The docs folder stores engineering and product documentation.

Current documentation:

* PRD.md
* SYSTEM_ARCHITECTURE.md
* AGENT_WORKFLOW_MAP.md
* PROJECT_STRUCTURE.md
* DATABASE_SCHEMA.md
* LANGGRAPH_WORKFLOW.md
* API_DESIGN.md

Future documentation may include:

* API_REFERENCE.md
* DEPLOYMENT_GUIDE.md
* CONTRIBUTING.md
* AGENT_REGISTRY.md
* OBSERVABILITY_GUIDE.md

---

# 15. Architecture Principles

The project follows these engineering principles:

* modularity
* supervisor-based orchestration
* specialist agent isolation
* separation of concerns
* workflow observability
* stateful orchestration
* provider abstraction
* controlled tool execution
* human approval for sensitive actions
* persistence-first workflow design
* scalable architecture boundaries

---

# 16. Engineering Philosophy

The MVP intentionally prioritizes:

* workflow clarity
* engineering simplicity
* observability
* maintainability
* modular architecture
* provider flexibility
* safe AI execution
* deterministic routing
* limited agent scope

over:

* premature optimization
* excessive autonomy
* uncontrolled agent spawning
* provider-specific workflow coupling
* enterprise-scale infrastructure

The system is designed to evolve incrementally into a more enterprise-ready architecture over future phases.

---

# 17. Repository Design Summary

The repository structure mirrors the supervisor-based multi-agent architecture directly.

The structure is designed to support:

* clean orchestration boundaries
* isolated specialist agents
* modular workflow routing
* observable execution
* provider flexibility
* future enterprise scaling

The repository intentionally separates:

* orchestration logic
* specialist agents
* tools
* memory
* provider abstraction
* workflow state
* monitoring
* persistence

This improves:

* debugging
* maintainability
* onboarding of contributors
* architecture readability
* workflow reliability
* portfolio quality
