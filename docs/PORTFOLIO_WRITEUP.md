# Portfolio Writeup

## Project Summary

Onboarding Buddy is an AI-assisted employee onboarding workflow tool. It helps HR teams create employee onboarding records, generate structured onboarding plans, and review task ownership and approval requirements through a usable dashboard.

The project demonstrates how multi-agent orchestration can be applied to a practical business workflow while preserving reliability, validation, and human oversight.

## Problem

Employee onboarding often depends on repeated manual coordination across HR, IT, managers, and new hires. Missing steps can create delays, inconsistent onboarding experiences, and poor visibility into task ownership.

## Solution

Onboarding Buddy uses a supervisor-based LangGraph workflow to coordinate specialized agents:

- Supervisor Agent routes the workflow.
- Intake Agent validates employee data.
- Task Planning Agent generates structured onboarding tasks.

The Streamlit frontend gives HR a simple operational dashboard for creating employees, generating plans, and reviewing tasks.

## Technical Highlights

- FastAPI backend with clear endpoint boundaries
- Streamlit frontend with dashboard metrics and task review
- LangGraph orchestration with deterministic routing safeguards
- OpenRouter integration for configurable LLM task generation
- SQLite persistence for employees and onboarding tasks
- Structured validation of LLM-generated task plans
- Fallback task generation when LLM output is unavailable or invalid
- pytest coverage for agent parsing and validation behavior

## Scope Discipline

The project keeps Phase 1 focused on:

- Create employee
- Generate onboarding plan
- View employee directory
- View generated tasks
- Show workflow and task status

Policy retrieval, approvals, audit logs, and follow-up agents are documented as roadmap items rather than mixed into the Phase 1 implementation.

## Outcome

The final result is a portfolio-ready AI workflow product that shows backend architecture, agent orchestration, frontend UX, persistence, validation, and practical product judgment.
