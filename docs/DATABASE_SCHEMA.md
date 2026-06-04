# Database Schema

## Current Database Support

The current runtime database supports:

- PostgreSQL through `DATABASE_URL`
- local PostgreSQL through `docker-compose.yml`
- Render PostgreSQL through the Render Internal Database URL

The active database is selected in `database/db.py`. If `DATABASE_URL` is missing, the app defaults to the local Docker Compose PostgreSQL URL.

## Tables

### `employees`

Stores employee onboarding records.

Important fields:

- `employee_id`
- `employee_name`
- `employee_email`
- `role`
- `department`
- `joining_date`
- `onboarding_status`
- `created_at`
- `updated_at`

### `users`

Stores authenticated application users.

Important fields:

- `user_id`
- `name`
- `email`
- `password_hash`
- `role`
- `employee_id`
- `manager_id`
- `created_at`
- `updated_at`

Valid roles:

```text
employee
manager
hr_admin
admin
```

`employee_id` links a login to an employee onboarding record. `manager_id` links direct reports to a manager user for manager-scoped access.

### `onboarding_tasks`

Stores generated onboarding tasks.

Important fields:

- `task_id`
- `employee_id`
- `task_name`
- `task_description`
- `task_status`
- `task_priority`
- `approval_required`
- `generated_by_agent`
- `assigned_owner`
- `created_at`
- `updated_at`

Valid task statuses:

```text
Pending
In Progress
Completed
Blocked
Failed
```

### `task_dependencies`

Stores upstream task relationships.

Important fields:

- `dependency_id`
- `employee_id`
- `task_id`
- `depends_on_task_id`
- `created_at`

The schema includes a unique constraint on `(task_id, depends_on_task_id)` to avoid duplicate dependencies.

### `approvals`

Stores approval records tied to onboarding tasks.

Important fields:

- `approval_id`
- `employee_id`
- `related_task_id`
- `action_type`
- `approval_status`
- `review_notes`
- `reviewed_by`
- `reviewed_at`
- `created_at`

Valid approval statuses:

```text
Awaiting Approval
Approved
Rejected
Revision Requested
```

### `audit_logs`

Stores workflow timeline events.

Important event types include:

- `approval_created`
- `approval_decision`
- `employee_updated`
- `workflow_plan_generated`
- `workflow_plan_requested`
- `task_status_updated`
- `task_start_blocked`
- `task_unlocked`
- `task_still_locked`

### `workflow_runs`

Stores durable workflow execution records.

Important fields:

- `workflow_run_id`
- `employee_id`
- `workflow_status`
- `current_node`
- `current_agent`
- `next_agent`
- `retry_count`
- `failure_reason`
- `started_at`
- `completed_at`
- `llm_provider`
- `llm_model`

### `agent_runs`

Stores agent execution summaries for each workflow run.

Important fields:

- `agent_run_id`
- `workflow_run_id`
- `employee_id`
- `agent_name`
- `agent_role`
- `execution_order`
- `input_summary`
- `output_summary`
- `routing_reason`
- `execution_status`
- `started_at`
- `completed_at`

### `workflow_state`

Reserved for future persisted workflow state snapshots. The current workflow persists workflow runs and agent runs, but does not yet use this table as a LangGraph checkpoint store.

### `knowledge_chunks`

Stores approved assistant knowledge chunks and deterministic local embeddings for vector-style retrieval.

Important fields:

- `chunk_id`
- `source`
- `title`
- `content`
- `content_hash`
- `embedding_json`
- `created_at`
- `updated_at`

The schema includes a unique constraint on `(source, content_hash)` so reindexing approved knowledge can update existing chunks without duplicating them.

## Indexes

The schema includes indexes for common operational reads:

- employee creation and onboarding status
- users by email, role, employee, and manager
- employee tasks
- task status
- task dependencies
- approvals by employee, task, and status
- audit logs by employee and workflow run
- workflow runs by employee and status
- agent runs by workflow run and employee
- knowledge chunks by source and content hash

## Repeatable Initialization

`schema.sql` uses `CREATE TABLE IF NOT EXISTS` and `CREATE INDEX IF NOT EXISTS`, so it can create missing tables and indexes repeatedly.

Important limitation:

```text
schema.sql does not migrate existing table definitions.
```

Alembic is not implemented yet. Add Alembic or dedicated migration scripts before making frequent deployed schema changes.
