# Implementation Roadmap

## Current Status

Phase 1 is complete.

Phase 2 MVP scope is implemented. Phase 3A and 3B are implemented as a constrained onboarding assistant and vector-RAG foundation.

- PostgreSQL support
- Render PostgreSQL deployment support
- task status management
- approval operations
- workflow run persistence
- agent run history
- workflow observability APIs
- task dependency enforcement
- locked/unlocked task state
- approval unlock logic
- timeline events
- frontend Operations workspace
- tests covering Phase 2 behavior
- approved-source onboarding assistant foundation
- role-aware assistant responses
- optional employee workflow context in assistant answers
- answer guardrails, confidence scoring, citations, and escalation behavior
- knowledge chunking, deterministic hashed embeddings, and PostgreSQL-backed vector index
- user authentication, JWT tokens, and RBAC foundation
- refresh token rotation
- tenant-aware access boundaries
- password reset token flow
- SSO assertion login foundation
- auth audit events
- Alembic migration scaffold

## Completed Phase 1

- project structure
- FastAPI backend
- Streamlit frontend
- initial local persistence
- employee creation and listing
- onboarding plan generation
- Supervisor Agent
- Intake Agent
- Task Planning Agent
- LangGraph workflow
- OpenRouter integration
- deterministic fallback task generation
- initial tests and documentation

## Completed Phase 2 MVP

### Persistence and Deployment

- PostgreSQL support through `DATABASE_URL`
- local PostgreSQL via Docker Compose
- Render PostgreSQL deployment support
- repeatable schema initialization with `schema.sql`

Alembic scaffolding is implemented. Use Alembic for deployed schema evolution and `schema.sql` for fresh local initialization.

### Workflow Operations

- approval queue
- approval decisions
- task status updates
- task dependency records
- dependency enforcement before `In Progress`
- approval unlock behavior
- blocked task state
- locked/unlocked task indicators
- workflow timeline events

### Observability

- workflow run records
- agent run records
- workflow run list API
- workflow run detail API
- employee timeline API
- Operations workspace workflow visibility

## Completed Phase 3A

### Strengthened Assistant Foundation

- `POST /assistant/chat`
- Streamlit Assistant tab
- approved local knowledge files under `knowledge/`
- stakeholder role normalization for Employee, Manager, HR, IT, and Security
- optional employee workflow context from existing repositories
- OpenRouter answer synthesis with deterministic source-grounded fallback
- insufficient-knowledge guardrails
- source citation metadata
- confidence scoring and labels
- escalation messages for low-confidence answers
- tests for fallback, role context, unsupported answers, and route behavior

## Completed Phase 3B

### Vector RAG Foundation

- approved knowledge document chunking
- deterministic local hashed embeddings
- cosine similarity retrieval
- PostgreSQL-backed `knowledge_chunks` table
- `POST /assistant/knowledge/reindex`
- retrieval mode reporting
- Streamlit source/citation display
- tests for chunk creation, indexing, confidence, and reindex routing

This is a real vector-RAG foundation for the project, but it deliberately avoids a network-dependent embedding provider. A production upgrade should evaluate external embeddings plus pgvector or a managed vector database.

## Completed Phase 4 Foundation

### Authentication And RBAC

- `users` table
- password hashing
- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`
- JWT bearer tokens
- refresh-token rotation
- password reset request and confirm flow
- SSO assertion login foundation
- tenant-aware user records
- auth audit logs
- Alembic migration scaffold
- authenticated user dependency
- roles: `employee`, `manager`, `hr_admin`, `admin`
- scoped employee, task, workflow, approval, assistant, and reindex access
- assistant role derived from authenticated user identity
- tests for token validation, role checks, employee access, manager access, and assistant role trust boundary

## Deployment Verification Checklist

Local PostgreSQL:

```bash
docker compose up -d
DATABASE_URL=postgresql://onboarding_buddy:onboarding_buddy@localhost:5432/onboarding_buddy
python -m database.db
```

Render backend Start Command:

```bash
python -m database.db && uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

Render environment variables:

```text
DATABASE_URL=<Render Internal Database URL>
OPENROUTER_API_KEY=<secret>
OPENROUTER_MODEL=openrouter/free
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
LANGSMITH_TRACING=false
APP_ENV=production
```

Streamlit Cloud secret:

```toml
API_BASE_URL = "https://onboarding-buddy-api.onrender.com"
```

## Recommended Next Milestones

After Phase 3A/3B are verified against deployment, the next architecture milestones should be:

1. Alembic migrations
2. real OAuth/OIDC provider integration
3. production secrets manager integration
4. database-level tenant enforcement and migration hardening
5. production embedding provider evaluation
6. pgvector or managed vector database migration
7. RAG retrieval and answer quality evaluation suite
8. role-based approval routing
9. background workers for long-running workflows
10. notification infrastructure
11. production observability stack
12. Policy/Knowledge Agent after assistant retrieval rules are stable

## Roadmap Only

These are not implemented yet:

- Policy/Knowledge Agent
- external embedding provider integration
- pgvector or managed vector database migration
- full RAG evaluation benchmark suite
- email or Slack notifications
- full OAuth/OIDC provider integration
- external production secrets manager
- calendar, chat, and HRMS integrations
- advanced audit dashboard
- Alembic migrations
- background workers
- multi-user roles
- production observability stack
