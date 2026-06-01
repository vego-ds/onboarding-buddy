# Onboarding Buddy

Onboarding Buddy is a supervisor-based multi-agent onboarding workflow platform that helps HR teams automate employee onboarding using LangGraph orchestration, configurable LLM routing through OpenRouter, human approvals, controlled tool execution, persistent workflow state, and production-grade observability.

The platform is designed around:

* multi-agent orchestration
* workflow reliability
* safe AI execution
* provider flexibility
* auditability
* human-in-the-loop operations
* enterprise-inspired onboarding workflows

---

# 1. Problem Statement

HR teams spend significant time managing repetitive onboarding tasks such as:

* creating onboarding checklists
* sending welcome emails
* collecting documents
* scheduling orientation
* notifying managers
* tracking onboarding progress

Manual onboarding workflows often create:

* delays
* inconsistent onboarding experiences
* missed onboarding steps
* low visibility into onboarding progress
* repetitive HR operations

Onboarding Buddy addresses these challenges through a supervisor-based multi-agent workflow system that coordinates onboarding planning, approval handling, workflow state management, task tracking, and observability.

---

# 2. Product Vision

Onboarding Buddy aims to become an intelligent onboarding operations platform that reduces repetitive HR workload, improves onboarding consistency, and creates a better employee onboarding experience through safe, observable, and modular multi-agent workflow automation.

---

# 3. Core Architecture Philosophy

The platform is intentionally designed as:

```text
Human-supervised multi-agent orchestration
```

not:

```text
fully autonomous AI execution
```

The architecture prioritizes:

* supervisor-controlled orchestration
* specialist agent isolation
* workflow observability
* approval-driven execution
* safe workflow automation
* persistent workflow state
* deterministic routing
* modular architecture

The system intentionally avoids:

* uncontrolled autonomous execution
* unrestricted tool access
* hidden workflow behavior
* excessive agent complexity
* provider-specific workflow coupling

---

# 4. Multi-Agent Architecture

The platform uses a supervisor-based multi-agent architecture.

The Supervisor Agent coordinates onboarding workflows and routes work to focused specialist agents.

---

## MVP Agents

| Agent                      | Responsibility                                 |
| -------------------------- | ---------------------------------------------- |
| Supervisor Agent           | Coordinates workflow routing and orchestration |
| Intake Agent               | Validates employee onboarding information      |
| Policy and Knowledge Agent | Retrieves onboarding policies and templates    |
| Task Planning Agent        | Generates onboarding checklist and task plans  |

---

## Deferred Phase 2 Agents

| Agent                   | Responsibility                         |
| ----------------------- | -------------------------------------- |
| Calendar Agent          | Schedules onboarding meetings          |
| Manager Follow-up Agent | Sends manager reminders and follow-ups |

The MVP intentionally limits the number of agents to keep workflow execution reliable, maintainable, and observable.

---

# 5. Key Features

* Employee onboarding form
* Supervisor-based multi-agent orchestration
* AI-generated onboarding checklist
* AI-generated welcome email draft
* Human-in-the-loop approval system
* Task status tracking
* Workflow state persistence
* Agent execution tracking
* Supervisor routing visibility
* Simulated tool execution
* Audit logging
* Workflow monitoring
* LangGraph orchestration
* OpenRouter-based configurable model routing
* Structured workflow validation
* Retry-safe workflow execution

---

# 6. Multi-Agent Workflow Overview

```text
HR Creates Employee Record
↓
Supervisor Agent Starts Workflow
↓
Supervisor Routes To Intake Agent
↓
Intake Agent Validates Employee Data
↓
Supervisor Routes To Policy & Knowledge Agent
↓
Policy Agent Retrieves Onboarding Context
↓
Supervisor Routes To Task Planning Agent
↓
Task Planning Agent Generates Checklist
↓
Supervisor Validates Outputs
↓
Tasks Saved To Database
↓
Welcome Email Generated
↓
HR Reviews Generated Content
↓
HR Approves or Rejects Actions
↓
Approved Tools Execute
↓
Workflow Logs Written
↓
Workflow Completes
```

---

# 7. System Architecture

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
┌──────────────────────────────┐
│      Specialist Agents       │
│                              │
│  - Intake Agent              │
│  - Policy & Knowledge Agent  │
│  - Task Planning Agent       │
└──────────────────────────────┘
↓
Shared Tools + Shared Memory
↓
SQLite Database + ChromaDB + Monitoring
↓
OpenRouter Provider Layer
```

---

# 8. Workflow Capabilities

The workflow system can:

* validate employee onboarding data
* retrieve onboarding templates
* retrieve onboarding policy context
* generate onboarding task plans
* generate welcome email drafts
* validate generated outputs
* pause safely for HR approval
* execute approved actions through controlled tools
* persist workflow state
* retry failed workflow steps safely
* preserve routing metadata
* track specialist agent execution history
* preserve provider and model metadata for debugging

The workflow is intentionally designed as a controlled orchestration system rather than an unrestricted autonomous AI system.

---

# 9. Human-In-The-Loop Design

Sensitive onboarding actions require HR approval before execution.

Examples include:

* sending official onboarding emails
* requesting sensitive employee documents
* triggering manager notifications
* marking onboarding as completed
* creating access-related tasks

This improves:

* safety
* accountability
* auditability
* trust
* workflow reliability

The workflow must never bypass approval requirements.

---

# 10. Guardrails and Failure Protection

The platform includes multiple guardrails to prevent unsafe, incorrect, or untraceable workflow execution.

Core guardrails include:

* human approval before sensitive actions
* supervisor-controlled routing
* structured validation of agent outputs
* controlled tool execution
* persisted workflow state
* finite retry limits
* audit logging
* routing visibility
* provider metadata tracking
* failure escalation to manual review
* environment-based secret management

---

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
Retry If Recoverable
↓
Escalate If Retry Limit Reached
↓
Require Manual Review
```

The workflow should never silently continue after critical failures.

---

# 11. Observability

The platform prioritizes workflow observability.

The system tracks:

* workflow execution
* supervisor routing decisions
* specialist agent execution
* retry activity
* approval states
* tool execution results
* provider request failures
* workflow failures
* workflow completion history
* configured model metadata

---

## Example Observable Events

* Supervisor Agent routed workflow to Intake Agent.
* Intake Agent detected missing joining date.
* Policy and Knowledge Agent retrieved onboarding template.
* Task Planning Agent generated onboarding checklist.
* Tool execution failed during orientation scheduling.
* OpenRouter request failed and retry was triggered.

---

## Observability Stack

| Component                  | Purpose                     |
| -------------------------- | --------------------------- |
| Python logging             | Backend logs                |
| SQLite audit logs          | Workflow activity history   |
| LangSmith                  | LangGraph execution tracing |
| Agent execution history    | Specialist agent visibility |
| OpenRouter metadata        | Provider observability      |
| Workflow state persistence | Workflow recovery           |

Observability is considered a mandatory infrastructure layer.

---

# 12. Tech Stack

| Layer                     | Technology                                 |
| ------------------------- | ------------------------------------------ |
| Frontend                  | Streamlit                                  |
| Backend                   | FastAPI                                    |
| Multi-Agent Orchestration | LangGraph                                  |
| Supervisor Routing        | Custom LangGraph routing                   |
| LLM Provider              | OpenRouter                                 |
| LLM Models                | Configurable through environment variables |
| Database                  | SQLite                                     |
| Vector Memory             | ChromaDB                                   |
| Monitoring                | Python logging, LangSmith, audit logs      |
| Validation                | Pydantic                                   |
| Workflow Persistence      | SQLite workflow state tables               |

---

# 13. Repository Structure

```text
onboarding-buddy/
│
├── frontend/
├── backend/
├── agents/
│   ├── supervisor/
│   ├── intake/
│   ├── policy/
│   ├── task_planning/
│   ├── knowledge/
│   ├── calendar/
│   ├── manager/
│   ├── shared/
│   └── workflow/
│
├── llm/
├── tools/
├── database/
├── memory/
├── monitoring/
├── schemas/
├── tests/
├── docs/
├── logs/
│
├── .env
├── requirements.txt
├── README.md
└── docker-compose.yml
```

The repository structure mirrors the supervisor-based multi-agent architecture directly.

---

# 14. Documentation

| Document                    | Purpose                        |
| --------------------------- | ------------------------------ |
| docs/PRD.md                 | Product requirements           |
| docs/SYSTEM_ARCHITECTURE.md | System architecture            |
| docs/AGENT_WORKFLOW_MAP.md  | Multi-agent workflow map       |
| docs/PROJECT_STRUCTURE.md   | Repository structure           |
| docs/DATABASE_SCHEMA.md     | Database schema                |
| docs/LANGGRAPH_WORKFLOW.md  | LangGraph orchestration design |
| docs/API_DESIGN.md          | API design                     |

---

# 15. API Overview

| Method | Endpoint                                          | Purpose                           |
| ------ | ------------------------------------------------- | --------------------------------- |
| POST   | /employees                                        | Create employee onboarding record |
| GET    | /employees/{employee_id}                          | Get employee details              |
| POST   | /employees/{employee_id}/generate-onboarding-plan | Trigger Supervisor Agent workflow |
| POST   | /employees/{employee_id}/generate-checklist       | Generate onboarding checklist     |
| POST   | /employees/{employee_id}/generate-email-draft     | Generate welcome email draft      |
| POST   | /approvals                                        | Submit approval decision          |
| PATCH  | /tasks/{task_id}/status                           | Update task status                |
| GET    | /employees/{employee_id}/status                   | Get onboarding workflow status    |
| GET    | /dashboard                                        | Get dashboard summary             |
| GET    | /audit-logs                                       | Get workflow audit logs           |
| GET    | /agent-runs                                       | Get agent execution history       |

---

# 16. MVP Scope

Version 1 focuses on:

* employee onboarding creation
* Supervisor Agent orchestration
* specialist agent execution
* onboarding checklist generation
* welcome email generation
* HR approval workflows
* workflow state persistence
* audit logging
* OpenRouter-configured model routing
* retry-safe workflow execution
* observability and tracing

---

## Deferred Features

The MVP intentionally defers:

* real HRMS integration
* payroll integration
* real document verification
* real access provisioning
* enterprise authentication
* advanced role-based access control
* distributed agent execution
* advanced multi-agent collaboration
* enterprise governance tooling

The goal is to validate the architecture first before increasing operational complexity.

---

# 17. Setup Instructions

## 1. Clone Repository

```bash
git clone https://github.com/your-username/onboarding-buddy.git
cd onboarding-buddy
```

---

## 2. Create Virtual Environment

```bash
python -m venv venv
```

---

## 3. Activate Virtual Environment

Windows:

```bash
venv\Scripts\activate
```

Mac/Linux:

```bash
source venv/bin/activate
```

---

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 5. Create Environment File

Create a `.env` file:

```text
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=openai/gpt-4.1
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
LANGSMITH_API_KEY=your_langsmith_api_key
DATABASE_URL=sqlite:///onboarding_buddy.db
```

---

## 6. Run Backend

```bash
uvicorn backend.main:app --reload
```

---

## 7. Run Frontend

```bash
streamlit run frontend/app.py
```

---

# 18. Engineering Principles

The platform is designed around:

* supervisor-based orchestration
* stateful workflow execution
* specialist agent isolation
* human-in-the-loop approvals
* workflow observability
* provider abstraction
* controlled tool execution
* auditability
* modular architecture
* deterministic routing
* persistence-first workflow design

Onboarding Buddy demonstrates how multi-agent AI systems can support structured enterprise workflows through:

* LangGraph orchestration
* persistent workflow state
* specialist agent coordination
* configurable model routing
* controlled tool execution
* workflow observability
* human-supervised execution

---

# 19. Architecture Positioning

This project is intentionally positioned as:

```text
A production-inspired supervisor-based multi-agent workflow system
```

rather than:

```text
A simple chatbot wrapper
```

The architecture demonstrates:

* LangGraph orchestration
* workflow state management
* agent coordination
* observability infrastructure
* provider abstraction
* routing systems
* approval systems
* workflow persistence
* AI workflow engineering patterns

This positioning significantly improves the project's relevance for:

* AI engineering roles
* agentic AI systems
* workflow orchestration systems
* enterprise AI applications
* platform engineering discussions
* system design interviews

---

# 20. Planned Roadmap Enhancements

Future roadmap enhancements include:

* real email integration
* Google Calendar integration
* Outlook integration
* Slack integration
* Microsoft Teams integration
* HRMS integration
* employee FAQ chatbot
* analytics dashboard
* PostgreSQL migration
* role-based access control
* multi-company onboarding support
* provider abstraction beyond OpenRouter
* distributed workflow execution
* advanced agent collaboration
* deployed public demo

---

# 21. Project Status

Current Status:

```text
Architecture and workflow implementation phase
```

Completed documentation:

* PRD
* System Architecture
* Agent Workflow Map
* Project Structure
* Database Schema
* LangGraph Workflow
* API Design

Next Phase:

```text
Implementation Roadmap and MVP Build
```

---

# 22. Why This Project Matters

Most AI portfolio projects stop at:

* chatbot wrappers
* prompt engineering demos
* single-agent prototypes

Onboarding Buddy is intentionally designed differently.

This project demonstrates:

* multi-agent orchestration
* stateful workflow execution
* LangGraph workflow engineering
* workflow persistence
* approval systems
* observability infrastructure
* provider abstraction
* retry-safe execution
* production-inspired architecture

The goal is to demonstrate practical AI systems engineering instead of isolated prompt demos.

---

# 23. License

MIT License