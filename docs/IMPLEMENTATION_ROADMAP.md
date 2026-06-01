# Onboarding Buddy Implementation Roadmap

## 1. Roadmap Objective

This roadmap defines the engineering execution strategy for delivering the Onboarding Buddy MVP as a supervisor-based multi-agent onboarding workflow platform.

The roadmap is structured to support:

* incremental platform delivery
* architecture stability
* workflow reliability
* controlled AI orchestration
* maintainable implementation
* production-aware engineering practices
* supervisor-based routing
* specialist agent execution
* workflow observability

The implementation strategy prioritizes:

* foundational stability
* workflow state persistence
* supervisor routing correctness
* agent isolation
* workflow observability
* controlled execution
* modular scalability
* engineering clarity

over:

* premature optimization
* unnecessary infrastructure complexity
* excessive autonomous behavior
* uncontrolled agent spawning
* over-engineering during MVP stages

---

# 2. Delivery Strategy

The platform will be implemented incrementally using milestone-driven engineering execution.

The delivery sequence follows:

```text
Engineering Foundation
↓
Persistence Layer
↓
Backend Service Layer
↓
LangGraph Orchestration Foundation
↓
Supervisor Agent
↓
Specialist Agents
↓
Agent Output Validation
↓
Controlled Tool Execution
↓
Human Approval Workflow
↓
Observability Infrastructure
↓
Frontend Operations Interface
↓
Testing & Validation
↓
Deployment
↓
Portfolio Packaging
```

The implementation intentionally avoids simultaneous feature development in order to preserve:

* architectural consistency
* debugging simplicity
* workflow traceability
* development velocity
* routing clarity
* agent execution visibility

---

# 3. Multi-Agent MVP Scope Strategy

The MVP should prove the core multi-agent architecture without overbuilding the system.

## MVP Agents

| Agent                      | Status       | Purpose                                      |
| -------------------------- | ------------ | -------------------------------------------- |
| Supervisor Agent           | Build in MVP | Routes and coordinates workflow execution    |
| Intake Agent               | Build in MVP | Validates employee onboarding information    |
| Policy and Knowledge Agent | Build in MVP | Retrieves onboarding context and templates   |
| Task Planning Agent        | Build in MVP | Generates onboarding checklist and task plan |

## Deferred Agents

| Agent                   | Phase   | Reason Deferred                                                    |
| ----------------------- | ------- | ------------------------------------------------------------------ |
| Calendar Agent          | Phase 2 | Real scheduling and calendar logic add integration complexity      |
| Manager Follow-up Agent | Phase 2 | Follow-up automation is not required to prove the MVP architecture |

The MVP must not build all agents immediately.

The first version should prove this pattern:

```text
Supervisor Agent
↓
Specialist Agent
↓
Structured Output
↓
Validation
↓
Tool Execution
↓
Observability
```

---

# 4. Why Agents Are Introduced Incrementally

Agents should be introduced one at a time because multi-agent systems become difficult to debug when too many agents are added too early.

Adding all agents immediately creates:

* routing complexity
* larger workflow state
* harder debugging
* unclear failure ownership
* more retry paths
* more output validation cases
* more tool integration risk
* higher implementation overhead

The correct strategy is:

```text
Build Supervisor
↓
Add Intake Agent
↓
Validate Routing
↓
Add Policy Agent
↓
Validate Context Retrieval
↓
Add Task Planning Agent
↓
Validate Generated Checklist
↓
Only Then Add More Agents
```

This keeps the architecture believable, maintainable, and production-aware.

---

# 5. Milestone 1: Engineering Foundation Setup

## Objective

Establish the repository structure, development environment, dependency management, and engineering standards.

---

## Implementation Scope

* Initialize GitHub repository
* Configure project structure
* Initialize Python virtual environment
* Configure dependency management
* Configure environment variable management
* Configure `.gitignore`
* Establish documentation structure
* Initialize repository standards
* Add placeholder folders for MVP and deferred agents

---

## Core Deliverables

* operational repository structure
* development environment configured
* dependency installation operational
* documentation structure finalized
* agent folder structure created

---

## Dependencies

None.

---

## Risks

| Risk                              | Mitigation                                       |
| --------------------------------- | ------------------------------------------------ |
| inconsistent repository structure | establish structure before implementation        |
| dependency conflicts              | isolate dependencies through virtual environment |
| unclear agent ownership           | create agent-specific folders from the start     |

---

## Completion Criteria

* repository initializes successfully
* dependencies install correctly
* documentation structure operational
* environment configuration validated
* agent folder structure matches architecture documents

---

# 6. Milestone 2: Persistence Layer Implementation

## Objective

Implement persistent workflow storage and onboarding data management.

---

## Implementation Scope

* Configure SQLite database
* Implement database connection layer
* Create database schema
* Implement persistence repositories
* Configure workflow persistence
* Configure audit persistence
* Configure retry persistence
* Configure agent run persistence
* Configure workflow state persistence

---

## Database Tables

* employees
* onboarding_tasks
* approvals
* audit_logs
* workflow_runs
* agent_runs
* workflow_state

---

## Core Deliverables

* operational persistence layer
* workflow state persistence
* audit logging persistence
* agent execution persistence
* repository abstraction layer
* retry metadata storage

---

## Dependencies

* Milestone 1 completed

---

## Risks

| Risk                        | Mitigation                                                                 |
| --------------------------- | -------------------------------------------------------------------------- |
| inconsistent workflow state | persist critical workflow context                                          |
| schema instability          | finalize schema before workflow integration                                |
| missing agent metadata      | include agent_name, agent_role, routing_reason, and execution_status early |

---

## Completion Criteria

* database initializes successfully
* onboarding records persist correctly
* audit logs persist correctly
* agent run records persist correctly
* workflow state recoverable after restart
* workflow run metadata is queryable

---

# 7. Milestone 3: Backend Service Layer Implementation

## Objective

Implement the FastAPI backend and service orchestration layer.

---

## Implementation Scope

* Initialize FastAPI application
* Configure API routing
* Configure request validation
* Configure response schemas
* Connect persistence layer
* Implement onboarding APIs
* Configure middleware
* Implement health check endpoints
* Implement workflow run APIs
* Implement agent run visibility APIs

---

## Initial Service Endpoints

```text
POST /employees
GET /employees/{employee_id}
GET /dashboard
GET /agent-runs
GET /workflow-runs/{workflow_run_id}
```

---

## Core Deliverables

* operational backend services
* validated request handling
* database-connected APIs
* structured API responses
* workflow and agent visibility endpoints

---

## Dependencies

* Milestone 2 completed

---

## Risks

| Risk                        | Mitigation                                                   |
| --------------------------- | ------------------------------------------------------------ |
| inconsistent API contracts  | enforce schema validation                                    |
| service-layer coupling      | isolate orchestration responsibilities                       |
| exposing too many internals | expose safe workflow summaries instead of raw internal state |

---

## Completion Criteria

* APIs respond successfully
* backend connects to persistence layer
* onboarding record creation operational
* validation errors handled consistently
* workflow run details retrievable
* agent run history retrievable

---

# 8. Milestone 4: LangGraph Orchestration Foundation

## Objective

Implement LangGraph workflow state management and orchestration infrastructure.

---

## Implementation Scope

* Implement workflow state schema
* Configure LangGraph workflow graph
* Configure base nodes
* Configure conditional routing infrastructure
* Configure workflow persistence
* Configure workflow lifecycle management
* Configure failure handling foundation
* Configure approval pause foundation

---

## Workflow State Areas

* onboarding context
* workflow execution status
* current node
* current agent
* next agent
* supervisor routing reason
* retry tracking
* approval tracking
* node transition tracking
* agent execution history
* workflow completion state

---

## Core Deliverables

* operational LangGraph workflow graph
* persistent workflow state
* routing infrastructure
* workflow lifecycle orchestration
* state transition logging

---

## Dependencies

* Milestone 3 completed

---

## Risks

| Risk                         | Mitigation                                            |
| ---------------------------- | ----------------------------------------------------- |
| state inconsistency          | enforce explicit state transitions                    |
| workflow routing instability | isolate routing logic                                 |
| unclear agent transitions    | persist current_agent, next_agent, and routing_reason |

---

## Completion Criteria

* workflow initializes correctly
* state transitions operate consistently
* workflow persistence operational
* conditional routing foundation functional
* workflow state includes agent metadata

---

# 9. Milestone 5: Supervisor Agent Implementation

## Objective

Implement the Supervisor Agent as the central workflow coordinator.

---

## Implementation Scope

* Implement Supervisor Agent module
* Implement agent registry
* Implement routing decision logic
* Implement supervisor prompts
* Implement routing reason generation
* Implement workflow state update logic
* Implement failure routing logic
* Implement approval routing logic
* Persist supervisor routing decisions

---

## Supervisor Responsibilities

* read workflow state
* decide next agent
* route work to specialist agents
* validate workflow order
* collect specialist outputs
* check approval requirements
* handle retry decisions
* route failures safely
* prepare workflow summaries

---

## Core Deliverables

* operational Supervisor Agent
* agent registry
* routing engine
* routing metadata persistence
* workflow state updates controlled by supervisor

---

## Dependencies

* Milestone 4 completed

---

## Risks

| Risk                           | Mitigation                                                  |
| ------------------------------ | ----------------------------------------------------------- |
| incorrect routing              | create explicit routing rules and tests                     |
| supervisor doing too much work | keep supervisor focused on coordination, not task execution |
| hidden routing decisions       | persist routing_reason in workflow state and audit logs     |

---

## Completion Criteria

* Supervisor Agent can route to registered agents
* Supervisor Agent rejects unknown agent routes
* routing decisions are logged
* routing metadata persists correctly
* workflow can stop safely on invalid routing

---

# 10. Milestone 6: Intake Agent Implementation

## Objective

Implement the first specialist agent for employee data validation.

---

## Implementation Scope

* Implement Intake Agent module
* Implement required field validation
* Implement employee profile normalization
* Implement missing data detection
* Implement structured intake output
* Persist intake execution in agent_runs

---

## Intake Agent Responsibilities

* validate employee name
* validate employee email
* validate role
* validate department
* validate joining date
* return missing fields
* return normalized employee profile

---

## Core Deliverables

* operational Intake Agent
* structured validation output
* agent execution logging
* missing field handling

---

## Dependencies

* Milestone 5 completed

---

## Risks

| Risk                                 | Mitigation                                      |
| ------------------------------------ | ----------------------------------------------- |
| incomplete validation                | define required fields clearly                  |
| inconsistent output                  | enforce structured response schema              |
| workflow continues with missing data | Supervisor must stop workflow when intake fails |

---

## Completion Criteria

* Intake Agent validates complete employee records
* Intake Agent detects missing fields
* Supervisor routes correctly after intake success or failure
* Intake execution appears in agent_runs

---

# 11. Milestone 7: Policy and Knowledge Agent Implementation

## Objective

Implement onboarding policy and knowledge retrieval.

---

## Implementation Scope

* Implement Policy and Knowledge Agent module
* Configure static onboarding templates
* Configure ChromaDB memory layer
* Implement role-based template retrieval
* Implement fallback default template
* Implement structured policy context output
* Persist policy agent execution in agent_runs

---

## Policy and Knowledge Agent Responsibilities

* retrieve onboarding templates
* retrieve role-based onboarding context
* retrieve company policy snippets
* prepare planning context
* fallback to default templates when needed

---

## Core Deliverables

* operational Policy and Knowledge Agent
* onboarding template retrieval
* policy context output
* fallback behavior
* memory retrieval integration

---

## Dependencies

* Milestone 6 completed

---

## Risks

| Risk                        | Mitigation                                          |
| --------------------------- | --------------------------------------------------- |
| empty policy retrieval      | provide default onboarding template                 |
| overcomplex memory setup    | start with static templates before vector retrieval |
| hallucinated policy context | restrict outputs to retrieved or default templates  |

---

## Completion Criteria

* policy context can be retrieved
* role-based template can be returned
* fallback template works
* policy execution appears in agent_runs
* Supervisor routes correctly after policy retrieval

---

# 12. Milestone 8: Task Planning Agent Implementation

## Objective

Implement onboarding checklist generation through the Task Planning Agent.

---

## Implementation Scope

* Implement Task Planning Agent module
* Implement checklist generation prompts
* Integrate OpenRouter model calls
* Use validated employee profile
* Use policy and knowledge context
* Generate structured checklist output
* Mark approval-required tasks
* Persist task planning execution in agent_runs

---

## Task Planning Agent Responsibilities

* generate onboarding checklist
* recommend task ordering
* identify task priority
* identify approval-required actions
* suggest task ownership
* return structured task plan

---

## Core Deliverables

* operational Task Planning Agent
* generated onboarding checklist
* structured task output
* approval flags
* task ownership metadata

---

## Dependencies

* Milestone 7 completed

---

## Risks

| Risk                      | Mitigation                             |
| ------------------------- | -------------------------------------- |
| malformed model output    | enforce structured response validation |
| generic checklist quality | use role and policy context            |
| unsafe tasks generated    | mark sensitive tasks for approval      |

---

## Completion Criteria

* Task Planning Agent generates checklist successfully
* output includes approval_required flags
* output validates against schema
* task planning execution appears in agent_runs
* Supervisor receives structured output

---

# 13. Milestone 9: Agent Output Validation Layer

## Objective

Implement validation for specialist agent outputs before persistence or tool execution.

---

## Implementation Scope

* Implement structured output validation
* Validate checklist task schema
* Validate missing fields
* Validate approval flags
* Detect duplicate tasks
* Detect empty or malformed outputs
* Configure retry behavior for invalid outputs

---

## Validation Areas

* Intake Agent output
* Policy and Knowledge Agent output
* Task Planning Agent output
* email draft output
* tool execution output

---

## Core Deliverables

* response validation layer
* output parser
* validation failure routing
* retry-safe validation behavior

---

## Dependencies

* Milestone 8 completed

---

## Risks

| Risk                        | Mitigation                                |
| --------------------------- | ----------------------------------------- |
| invalid outputs reach tools | validate before persistence and execution |
| excessive retries           | enforce finite retry limits               |
| unclear validation failures | log validation errors clearly             |

---

## Completion Criteria

* invalid agent outputs are rejected
* valid outputs proceed to persistence
* retry behavior works correctly
* validation failures are logged and observable

---

# 14. Milestone 10: Controlled Tool Execution Layer

## Objective

Implement controlled and observable workflow tool execution.

---

## Tooling Components

* checklist_tool.py
* email_tool.py
* approval_tool.py
* task_tool.py
* logging_tool.py
* calendar_tool.py
* notification_tool.py

---

## Implementation Scope

* implement isolated tool interfaces
* validate tool input handling
* configure structured tool responses
* integrate workflow tool invocation
* configure tool-level observability
* persist tool execution results
* preserve agent source metadata

---

## Core Deliverables

* operational tool execution layer
* observable tool invocation
* structured execution responses
* failure-safe tool handling
* tool execution metadata

---

## Dependencies

* Milestone 9 completed

---

## Risks

| Risk                        | Mitigation                                            |
| --------------------------- | ----------------------------------------------------- |
| uncontrolled tool execution | enforce workflow-controlled invocation                |
| invalid tool responses      | validate structured outputs                           |
| tools bypass approval       | require approval checks before sensitive tool actions |

---

## Completion Criteria

* tools execute correctly
* workflow invokes tools safely
* tool failures observable
* tool responses persisted correctly
* sensitive tools require approval

---

# 15. Milestone 11: Human Approval Workflow

## Objective

Implement approval workflows for sensitive onboarding actions.

---

## Implementation Scope

* Implement approval records
* Implement approval APIs
* Implement approval pause behavior
* Implement approval status persistence
* Implement approval routing
* Implement rejection and revision handling
* Integrate approval checks before tool execution

---

## Approval Required For

* sending official onboarding emails
* requesting sensitive employee documents
* triggering manager notifications
* marking onboarding as completed
* creating access-related tasks

---

## Core Deliverables

* operational approval workflow
* persisted approval decisions
* workflow pause and resume behavior
* approval-aware tool execution

---

## Dependencies

* Milestone 10 completed

---

## Risks

| Risk                       | Mitigation                                       |
| -------------------------- | ------------------------------------------------ |
| workflow bypasses approval | enforce approval checks before tools             |
| approval state lost        | persist approval state in database               |
| unclear rejection behavior | implement explicit rejection and revision routes |

---

## Completion Criteria

* HR can approve, reject, or request revision
* approval decisions persist correctly
* workflow pauses while approval is pending
* approved actions continue to tool execution
* rejected actions stop or reroute safely

---

# 16. Milestone 12: Observability Infrastructure

## Objective

Implement workflow monitoring, auditability, routing visibility, and tracing infrastructure.

---

## Observability Components

* Python logging
* audit logging
* LangSmith tracing
* retry visibility
* node transition visibility
* workflow execution visibility
* supervisor routing visibility
* specialist agent execution visibility
* provider metadata visibility

---

## Implementation Scope

* configure backend logging
* configure workflow tracing
* configure audit infrastructure
* expose retry visibility
* expose workflow transition tracking
* expose agent execution history
* expose supervisor routing history
* persist provider and model metadata

---

## Core Deliverables

* operational observability infrastructure
* workflow traceability
* audit persistence
* failure visibility
* routing visibility
* agent execution history

---

## Dependencies

* Milestone 11 completed

---

## Risks

| Risk                              | Mitigation                             |
| --------------------------------- | -------------------------------------- |
| hidden workflow failures          | expose observable failure states       |
| insufficient debugging visibility | log critical workflow transitions      |
| unclear agent behavior            | persist agent_runs and routing reasons |

---

## Completion Criteria

* workflow activity observable
* retries visible
* failures traceable
* LangSmith tracing operational
* agent runs visible through API
* routing decisions visible in audit logs

---

# 17. Milestone 13: Workflow Operations Interface

## Objective

Implement the Streamlit-based onboarding operations interface.

---

## Interface Areas

* onboarding request form
* onboarding dashboard
* approval operations
* workflow visibility
* audit visibility
* task tracking interface
* agent activity interface
* routing trace view

---

## Implementation Scope

* connect frontend to APIs
* implement workflow visibility
* implement onboarding task displays
* implement approval operations
* implement audit visibility
* implement agent run visibility
* implement workflow status display

---

## Core Deliverables

* operational onboarding interface
* frontend-backend integration
* workflow operations visibility
* agent activity visibility

---

## Dependencies

* Milestone 12 completed

---

## Risks

| Risk                             | Mitigation                                  |
| -------------------------------- | ------------------------------------------- |
| frontend-backend coupling        | enforce API-only communication              |
| inconsistent workflow visibility | expose workflow state explicitly            |
| overwhelming UI                  | keep agent activity readable and summarized |

---

## Completion Criteria

* onboarding requests operational
* approvals operational
* workflow visibility functional
* dashboard updates correctly
* agent activity is visible to user

---

# 18. Milestone 14: Workflow Validation & Testing

## Objective

Validate workflow reliability, routing correctness, agent execution, and execution safety.

---

## Validation Areas

* API validation
* Supervisor Agent routing
* Intake Agent validation
* Policy and Knowledge Agent retrieval
* Task Planning Agent checklist generation
* agent output validation
* workflow execution
* retry handling
* approval routing
* tool execution
* persistence validation
* failure handling

---

## Implementation Scope

* implement unit tests
* implement workflow tests
* validate routing logic
* validate retry behavior
* validate persistence consistency
* validate tool execution
* validate approval boundaries
* validate agent output schemas

---

## Core Deliverables

* automated validation suite
* validated workflow behavior
* validated routing behavior
* retry-safe execution validation
* validated agent outputs

---

## Dependencies

* Milestone 13 completed

---

## Risks

| Risk                          | Mitigation                        |
| ----------------------------- | --------------------------------- |
| workflow instability          | validate critical workflow paths  |
| inconsistent failure handling | test retry and escalation logic   |
| routing bugs                  | test supervisor routing decisions |

---

## Completion Criteria

* workflow execution validated
* APIs behave consistently
* retries validated
* workflow failures handled safely
* Supervisor routing validated
* specialist agents validated

---

# 19. Milestone 15: Deployment & Runtime Delivery

## Objective

Deploy the MVP for operational demonstration and portfolio visibility.

---

## Implementation Scope

* configure Docker environment
* configure deployment runtime
* deploy backend services
* deploy frontend services
* configure environment variables
* validate production startup behavior
* validate deployed workflow execution

---

## Candidate Platforms

* Render
* Railway
* Hugging Face Spaces
* AWS
* Azure

---

## Core Deliverables

* publicly accessible MVP
* deployment-ready infrastructure
* runtime documentation
* operational demo workflow

---

## Dependencies

* Milestone 14 completed

---

## Risks

| Risk                             | Mitigation                                          |
| -------------------------------- | --------------------------------------------------- |
| deployment configuration issues  | isolate runtime configuration                       |
| environment inconsistencies      | validate environment variables                      |
| OpenRouter configuration failure | verify provider keys and model config in deployment |

---

## Completion Criteria

* deployed application accessible
* backend operational
* frontend operational
* workflow executes successfully in deployed environment
* environment variables configured safely

---

# 20. Milestone 16: Repository & Portfolio Packaging

## Objective

Finalize repository quality and engineering presentation standards.

---

## Implementation Scope

* finalize README
* organize architecture documentation
* add architecture visuals
* add workflow screenshots
* add agent workflow diagrams
* add demo assets
* improve repository navigation
* clean repository structure
* verify docs are internally consistent

---

## Core Deliverables

* portfolio-grade repository
* professional engineering presentation
* architecture documentation package
* recruiter-readable project narrative

---

## Dependencies

* Milestone 15 completed

---

## Risks

| Risk                         | Mitigation                                    |
| ---------------------------- | --------------------------------------------- |
| unclear project presentation | prioritize engineering clarity                |
| documentation inconsistency  | align all architecture documents              |
| project appears too complex  | clearly explain MVP scope and deferred agents |

---

## Completion Criteria

* repository professionally organized
* architecture clearly documented
* workflow visually understandable
* documentation internally consistent
* README clearly explains project value

---

# 21. Milestone 17: Public Launch & Technical Positioning

## Objective

Prepare the project for public technical presentation and professional visibility.

---

## Implementation Scope

* prepare architecture visuals
* prepare workflow visuals
* prepare deployment screenshots
* record workflow demonstration
* prepare technical launch post
* prepare engineering explanation assets
* prepare recruiter-facing project summary

---

## Core Deliverables

* LinkedIn launch assets
* project showcase materials
* technical presentation assets
* public demo narrative

---

## Dependencies

* Milestone 16 completed

---

## Risks

| Risk                              | Mitigation                                                                                   |
| --------------------------------- | -------------------------------------------------------------------------------------------- |
| weak technical positioning        | emphasize supervisor-based multi-agent architecture and observability                        |
| unclear system narrative          | align messaging with architecture decisions                                                  |
| overclaiming production readiness | describe it as production-inspired or portfolio-grade unless actually deployed in production |

---

## Completion Criteria

* technical launch assets finalized
* workflow architecture clearly communicated
* project presentation production-ready
* launch messaging aligned with actual implementation

---

# 22. MVP Scope Boundary

The MVP intentionally includes:

* Supervisor Agent
* Intake Agent
* Policy and Knowledge Agent
* Task Planning Agent
* employee record creation
* onboarding checklist generation
* welcome email draft generation
* approval workflow
* simulated tool execution
* workflow persistence
* agent execution tracking
* audit logs
* dashboard visibility

The MVP intentionally excludes:

* Calendar Agent
* Manager Follow-up Agent
* enterprise authentication
* production RBAC
* payroll integration
* real HRMS integration
* real document verification
* real access provisioning
* advanced analytics
* multi-tenant infrastructure
* production-scale orchestration infrastructure

These capabilities are intentionally deferred to future platform expansion phases.

---

# 23. Engineering Execution Principles

Implementation should continuously prioritize:

* modular architecture
* observable workflows
* isolated specialist agents
* supervisor-controlled routing
* isolated tool execution
* workflow reliability
* explicit state transitions
* maintainable orchestration
* deterministic workflow behavior
* safe failure handling

The implementation strategy intentionally favors:

* architecture stability
* workflow clarity
* operational traceability
* incremental validation

over:

* premature feature expansion
* excessive agent autonomy
* infrastructure over-engineering
* uncontrolled multi-agent complexity

---

# 24. Roadmap Summary

This roadmap transforms the platform from:

* architecture documentation
* workflow specifications
* orchestration design

into:

* executable workflow infrastructure
* supervisor-based multi-agent orchestration
* observable onboarding operations
* deployable AI workflow system
* production-aware onboarding automation architecture

The roadmap is intentionally structured to support:

* scalable engineering execution
* workflow-oriented AI system design
* maintainable implementation
* enterprise-inspired delivery practices
* portfolio-grade technical storytelling

The most important implementation principle is:

```text
Build the orchestration foundation first.
Add agents incrementally.
Validate each agent before expanding the system.
```
