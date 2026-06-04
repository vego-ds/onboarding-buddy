# Portfolio Writeup

## Project Summary

Onboarding Buddy is an AI-assisted workflow operations platform for employee onboarding. It helps HR teams create employee records, generate structured onboarding plans, manage approvals, enforce task dependencies, answer approved-source onboarding questions, and inspect workflow execution history through a usable operations dashboard.

## Problem

Employee onboarding requires coordination across HR, IT, managers, and new hires. Manual tracking creates missed steps, delayed access, unclear ownership, and poor visibility into workflow state.

## Solution

Onboarding Buddy uses a supervisor-based LangGraph workflow with focused agents:

- Supervisor Agent routes the workflow.
- Intake Agent validates employee data.
- Task Planning Agent generates structured onboarding tasks.

The FastAPI backend persists workflow runs, agent runs, tasks, approvals, dependencies, and timeline events. The Streamlit frontend gives HR an operations workspace for reviewing approvals, changing task status, and seeing locked/unlocked workflow state.

Phase 3 adds a constrained onboarding assistant that answers questions from approved local knowledge sources, optional employee workflow context, and a PostgreSQL-backed knowledge chunk index.

## Technical Highlights

- FastAPI backend with clear route boundaries
- Streamlit frontend with Operations workspace
- LangGraph orchestration with deterministic routing safeguards
- OpenRouter integration for configurable LLM task generation
- PostgreSQL persistence support
- Render PostgreSQL deployment support
- Workflow run persistence
- Agent run history
- Approval operations
- Task dependency enforcement
- Locked/unlocked task state
- Timeline events for auditability
- Approved-source onboarding assistant foundation
- Role-aware assistant responses
- Optional employee workflow context in assistant answers
- Answer guardrails, citations, confidence scoring, and escalation behavior
- Deterministic local embeddings and vector-style retrieval
- PostgreSQL-backed `knowledge_chunks` index
- Authentication and RBAC foundation
- JWT-backed user identity
- Assistant role derived from authenticated backend user
- pytest coverage for agents, repositories, route behavior, and database configuration

## Scope Discipline

Implemented now:

- employee CRUD/listing
- onboarding plan generation
- task lifecycle management
- approvals
- workflow observability
- dependency enforcement
- operations dashboard
- onboarding assistant foundation
- vector-RAG foundation over approved knowledge chunks
- authentication and RBAC foundation

Roadmap only:

- Policy/Knowledge Agent
- external embedding provider integration
- pgvector or managed vector database migration
- email or Slack notifications
- enterprise SSO
- multi-tenant organization isolation
- Alembic migrations
- background workers
- production observability stack

## Outcome

The project has moved from an AI planning demo into a credible workflow orchestration MVP. Phase 3 adds a controlled assistant plus vector-RAG foundation, and Phase 4 adds real user identity and RBAC. The next production milestones are migrations, enterprise SSO, external embedding evaluation, and deployment verification against live PostgreSQL.
