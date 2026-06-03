# Portfolio Writeup

## Project Summary

Onboarding Buddy is an AI-assisted workflow operations platform for employee onboarding. It helps HR teams create employee records, generate structured onboarding plans, manage approvals, enforce task dependencies, and inspect workflow execution history through a usable operations dashboard.

## Problem

Employee onboarding requires coordination across HR, IT, managers, and new hires. Manual tracking creates missed steps, delayed access, unclear ownership, and poor visibility into workflow state.

## Solution

Onboarding Buddy uses a supervisor-based LangGraph workflow with focused agents:

- Supervisor Agent routes the workflow.
- Intake Agent validates employee data.
- Task Planning Agent generates structured onboarding tasks.

The FastAPI backend persists workflow runs, agent runs, tasks, approvals, dependencies, and timeline events. The Streamlit frontend gives HR an operations workspace for reviewing approvals, changing task status, and seeing locked/unlocked workflow state.

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

Roadmap only:

- Policy/Knowledge Agent
- RAG/vector memory
- email or Slack notifications
- authentication and authorization
- Alembic migrations
- background workers
- production observability stack

## Outcome

The project has moved from an AI planning demo into a credible workflow orchestration MVP. Phase 2 is suitable to mark complete for MVP scope after deployment verification against a live PostgreSQL database.
