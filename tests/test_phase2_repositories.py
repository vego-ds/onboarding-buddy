import sqlite3

import pytest

from database.repositories import approval_repository, task_repository
from database.repositories import audit_repository, dependency_repository
from database.repositories import workflow_run_repository
from database.repositories import knowledge_repository


@pytest.fixture
def memory_connection(monkeypatch):
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript(
        """
        CREATE TABLE onboarding_tasks (
            task_id TEXT PRIMARY KEY,
            employee_id TEXT NOT NULL,
            task_name TEXT NOT NULL,
            task_description TEXT,
            task_status TEXT DEFAULT 'Pending',
            task_priority TEXT DEFAULT 'Medium',
            approval_required INTEGER DEFAULT 0,
            generated_by_agent TEXT,
            assigned_owner TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE approvals (
            approval_id TEXT PRIMARY KEY,
            employee_id TEXT NOT NULL,
            related_task_id TEXT,
            action_type TEXT NOT NULL,
            approval_status TEXT DEFAULT 'Awaiting Approval',
            review_notes TEXT,
            reviewed_by TEXT,
            reviewed_at TEXT,
            created_at TEXT NOT NULL
        );

        CREATE TABLE audit_logs (
            log_id TEXT PRIMARY KEY,
            employee_id TEXT,
            workflow_run_id TEXT,
            event_type TEXT NOT NULL,
            event_message TEXT NOT NULL,
            agent_name TEXT,
            routing_reason TEXT,
            event_status TEXT DEFAULT 'Success',
            timestamp TEXT NOT NULL
        );

        CREATE TABLE task_dependencies (
            dependency_id TEXT PRIMARY KEY,
            employee_id TEXT NOT NULL,
            task_id TEXT NOT NULL,
            depends_on_task_id TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE workflow_runs (
            workflow_run_id TEXT PRIMARY KEY,
            employee_id TEXT NOT NULL,
            workflow_status TEXT DEFAULT 'Running',
            current_node TEXT,
            current_agent TEXT,
            next_agent TEXT,
            retry_count INTEGER DEFAULT 0,
            failure_reason TEXT,
            started_at TEXT NOT NULL,
            completed_at TEXT,
            llm_provider TEXT DEFAULT 'OpenRouter',
            llm_model TEXT
        );

        CREATE TABLE agent_runs (
            agent_run_id TEXT PRIMARY KEY,
            workflow_run_id TEXT,
            employee_id TEXT,
            agent_name TEXT NOT NULL,
            agent_role TEXT NOT NULL,
            execution_order INTEGER,
            input_summary TEXT,
            output_summary TEXT,
            routing_reason TEXT,
            execution_status TEXT DEFAULT 'Success',
            retry_count INTEGER DEFAULT 0,
            execution_duration_ms INTEGER,
            llm_provider TEXT DEFAULT 'OpenRouter',
            llm_model TEXT,
            started_at TEXT NOT NULL,
            completed_at TEXT
        );

        CREATE TABLE knowledge_chunks (
            chunk_id TEXT PRIMARY KEY,
            source TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            content_hash TEXT NOT NULL,
            embedding_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE (source, content_hash)
        );
        """
    )

    monkeypatch.setattr(task_repository, "get_connection", lambda: connection)
    monkeypatch.setattr(approval_repository, "get_connection", lambda: connection)
    monkeypatch.setattr(audit_repository, "get_connection", lambda: connection)
    monkeypatch.setattr(dependency_repository, "get_connection", lambda: connection)
    monkeypatch.setattr(workflow_run_repository, "get_connection", lambda: connection)
    monkeypatch.setattr(knowledge_repository, "get_connection", lambda: connection)

    yield connection

    connection.close()


def test_create_task_approvals_only_creates_for_required_tasks(memory_connection):
    tasks = [
        {"task_id": "TASK_1", "task_name": "Sensitive task", "approval_required": True},
        {"task_id": "TASK_2", "task_name": "Routine task", "approval_required": False},
    ]

    approvals = approval_repository.create_task_approvals("emp_1", tasks)

    assert len(approvals) == 1
    assert approvals[0]["employee_id"] == "EMP_1"
    assert approvals[0]["related_task_id"] == "TASK_1"
    assert approvals[0]["approval_status"] == "Awaiting Approval"


def test_update_approval_decision(memory_connection):
    approval = approval_repository.create_approval(
        employee_id="EMP_1",
        related_task_id="TASK_1",
        action_type="Review task",
    )

    updated = approval_repository.update_approval_decision(
        approval["approval_id"],
        approval_status="Approved",
        review_notes="Looks good.",
        reviewed_by="Avery",
    )

    assert updated["approval_status"] == "Approved"
    assert updated["review_notes"] == "Looks good."
    assert updated["reviewed_by"] == "Avery"


def test_approval_lookup_normalizes_ids(memory_connection):
    approval = approval_repository.create_approval(
        employee_id="EMP_1",
        related_task_id="task_1",
        action_type="Review task",
    )

    fetched = approval_repository.get_approval_by_task_id(" task_1 ")
    updated = approval_repository.update_approval_decision(
        approval["approval_id"].lower(),
        approval_status="Approved",
    )

    assert fetched["approval_id"] == approval["approval_id"]
    assert fetched["related_task_id"] == "TASK_1"
    assert updated["approval_status"] == "Approved"


def test_update_approval_decision_rejects_invalid_status(memory_connection):
    approval = approval_repository.create_approval(
        employee_id="EMP_1",
        related_task_id="TASK_1",
        action_type="Review task",
    )

    with pytest.raises(ValueError, match="Invalid approval status"):
        approval_repository.update_approval_decision(
            approval["approval_id"],
            approval_status="Maybe",
        )


def test_update_task_status(memory_connection):
    task = task_repository.create_task(
        "EMP_1",
        {
            "task_name": "Send welcome email",
            "task_description": "Send a welcome email.",
            "task_status": "Pending",
            "task_priority": "High",
            "approval_required": True,
            "assigned_owner": "HR",
        },
    )

    updated = task_repository.update_task_status(task["task_id"], "Completed")

    assert updated["task_status"] == "Completed"


def test_task_lookup_and_status_update_normalize_task_id(memory_connection):
    task = task_repository.create_task(
        "EMP_1",
        {
            "task_name": "Send welcome email",
            "task_description": "Send a welcome email.",
        },
    )

    fetched = task_repository.get_task_by_id(f" {task['task_id'].lower()} ")
    updated = task_repository.update_task_status(
        task["task_id"].lower(),
        "Completed",
    )

    assert fetched["task_id"] == task["task_id"]
    assert updated["task_status"] == "Completed"


def test_update_task_status_rejects_invalid_status(memory_connection):
    task = task_repository.create_task(
        "EMP_1",
        {
            "task_name": "Send welcome email",
            "task_description": "Send a welcome email.",
        },
    )

    with pytest.raises(ValueError, match="Invalid task status"):
        task_repository.update_task_status(task["task_id"], "Maybe")


def test_task_cannot_start_until_dependency_is_completed(memory_connection):
    first_task = task_repository.create_task(
        "EMP_1",
        {
            "task_name": "Collect documents",
            "task_description": "Collect required documents.",
        },
    )
    second_task = task_repository.create_task(
        "EMP_1",
        {
            "task_name": "Prepare access",
            "task_description": "Prepare role access.",
        },
    )
    dependency_repository.create_task_dependency(
        employee_id="EMP_1",
        task_id=second_task["task_id"],
        depends_on_task_id=first_task["task_id"],
    )

    with pytest.raises(ValueError, match="Collect documents is Pending"):
        task_repository.update_task_status(second_task["task_id"], "In Progress")

    blocked_task = task_repository.get_task_by_id(second_task["task_id"])
    assert blocked_task["task_status"] == "Blocked"

    task_repository.update_task_status(first_task["task_id"], "Completed")
    unlocked_task = task_repository.get_task_by_id(second_task["task_id"])
    assert unlocked_task["task_status"] == "Pending"

    updated = task_repository.update_task_status(second_task["task_id"], "In Progress")

    assert updated["task_status"] == "In Progress"


def test_task_dependency_creation_is_idempotent(memory_connection):
    first_task = task_repository.create_task(
        "EMP_1",
        {
            "task_name": "Collect documents",
            "task_description": "Collect required documents.",
        },
    )
    second_task = task_repository.create_task(
        "EMP_1",
        {
            "task_name": "Prepare access",
            "task_description": "Prepare role access.",
        },
    )

    first_dependency = dependency_repository.create_task_dependency(
        employee_id="EMP_1",
        task_id=second_task["task_id"],
        depends_on_task_id=first_task["task_id"],
    )
    second_dependency = dependency_repository.create_task_dependency(
        employee_id="EMP_1",
        task_id=second_task["task_id"],
        depends_on_task_id=first_task["task_id"],
    )

    dependencies = dependency_repository.get_dependencies_for_task(
        second_task["task_id"]
    )

    assert first_dependency["dependency_id"] == second_dependency["dependency_id"]
    assert len(dependencies) == 1


def test_task_enforcement_state_reports_lock_reasons(memory_connection):
    first_task = task_repository.create_task(
        "EMP_1",
        {
            "task_name": "Collect documents",
            "task_description": "Collect required documents.",
        },
    )
    second_task = task_repository.create_task(
        "EMP_1",
        {
            "task_name": "Prepare access",
            "task_description": "Prepare role access.",
            "approval_required": True,
        },
    )
    dependency_repository.create_task_dependency(
        employee_id="EMP_1",
        task_id=second_task["task_id"],
        depends_on_task_id=first_task["task_id"],
    )
    approval_repository.create_approval(
        employee_id="EMP_1",
        related_task_id=second_task["task_id"],
        action_type="Review task",
    )

    enforcement = task_repository.get_task_enforcement_state(second_task["task_id"])

    assert enforcement["is_locked"] is True
    assert enforcement["can_start"] is False
    assert enforcement["dependency_count"] == 1
    assert enforcement["blocked_dependency_count"] == 1
    assert "approval is Awaiting Approval" in enforcement["lock_reasons"]
    assert "Collect documents is Pending" in enforcement["lock_reasons"]


def test_approval_required_task_cannot_start_until_approved(memory_connection):
    task = task_repository.create_task(
        "EMP_1",
        {
            "task_name": "Send welcome email",
            "task_description": "Send a welcome email.",
            "approval_required": True,
        },
    )
    approval = approval_repository.create_approval(
        employee_id="EMP_1",
        related_task_id=task["task_id"],
        action_type="Review task",
    )

    with pytest.raises(ValueError, match="approval is Awaiting Approval"):
        task_repository.update_task_status(task["task_id"], "In Progress")

    blocked_task = task_repository.get_task_by_id(task["task_id"])
    assert blocked_task["task_status"] == "Blocked"

    approval_repository.update_approval_decision(
        approval["approval_id"],
        approval_status="Approved",
    )
    unlocked_task = task_repository.get_task_by_id(task["task_id"])
    assert unlocked_task["task_status"] == "Pending"

    updated = task_repository.update_task_status(task["task_id"], "In Progress")

    assert updated["task_status"] == "In Progress"


def test_blocked_and_unlocked_tasks_write_timeline_events(memory_connection):
    task = task_repository.create_task(
        "EMP_1",
        {
            "task_name": "Provision admin access",
            "task_description": "Provision admin access.",
            "approval_required": True,
        },
    )
    approval = approval_repository.create_approval(
        employee_id="EMP_1",
        related_task_id=task["task_id"],
        action_type="Review task",
    )

    with pytest.raises(ValueError, match="approval is Awaiting Approval"):
        task_repository.update_task_status(task["task_id"], "In Progress")

    approval_repository.update_approval_decision(
        approval["approval_id"],
        approval_status="Approved",
    )
    logs = audit_repository.get_audit_logs(employee_id="EMP_1")
    event_types = [log["event_type"] for log in logs]

    assert "task_start_blocked" in event_types
    assert "task_unlocked" in event_types


def test_task_status_update_writes_audit_log(memory_connection):
    task = task_repository.create_task(
        "EMP_1",
        {
            "task_name": "Schedule orientation",
            "task_description": "Schedule orientation.",
        },
    )

    task_repository.update_task_status(task["task_id"], "Completed")
    logs = audit_repository.get_audit_logs(employee_id="EMP_1")

    assert logs[0]["event_type"] == "task_status_updated"
    assert "Completed" in logs[0]["event_message"]


def test_workflow_run_and_agent_runs_are_persisted(memory_connection):
    workflow_run = workflow_run_repository.create_workflow_run("EMP_1")
    final_run = workflow_run_repository.complete_workflow_run(
        workflow_run["workflow_run_id"],
        {
            "workflow_status": "COMPLETED",
            "current_agent": "supervisor",
            "next_agent": "complete",
        },
    )
    agent_runs = workflow_run_repository.create_agent_runs(
        workflow_run_id=workflow_run["workflow_run_id"],
        employee_id="EMP_1",
        agent_execution_history=[
            {
                "agent": "intake_agent",
                "status": "success",
                "summary": "Validated employee.",
            },
            {
                "agent": "task_planning_agent",
                "status": "skipped",
                "summary": "Existing tasks found.",
            },
        ],
    )

    assert final_run["workflow_status"] == "COMPLETED"
    assert final_run["completed_at"] is not None
    assert len(agent_runs) == 2
    assert agent_runs[0]["execution_order"] == 1


def test_workflow_run_can_be_fetched_by_workflow_run_id(memory_connection):
    workflow_run = workflow_run_repository.create_workflow_run("EMP_1")

    fetched = workflow_run_repository.get_workflow_run_by_id(
        workflow_run["workflow_run_id"]
    )

    assert fetched["workflow_run_id"] == workflow_run["workflow_run_id"]
    assert fetched["employee_id"] == "EMP_1"
    assert fetched["workflow_status"] == "Running"


def test_workflow_run_lookup_normalizes_lowercase_id(memory_connection):
    workflow_run = workflow_run_repository.create_workflow_run("EMP_1")

    fetched = workflow_run_repository.get_workflow_run_by_id(
        workflow_run["workflow_run_id"].lower()
    )

    assert fetched["workflow_run_id"] == workflow_run["workflow_run_id"]


def test_workflow_run_lookup_returns_none_for_missing_run(memory_connection):
    assert workflow_run_repository.get_workflow_run_by_id("WF_MISSING") is None


def test_workflow_run_listing_filters_by_employee(memory_connection):
    workflow_run_repository.create_workflow_run("EMP_1")
    workflow_run_repository.create_workflow_run("EMP_2")

    runs = workflow_run_repository.get_workflow_runs(employee_id="EMP_1")

    assert len(runs) == 1
    assert runs[0]["employee_id"] == "EMP_1"


def test_agent_runs_are_fetched_for_normalized_workflow_run_id(memory_connection):
    workflow_run = workflow_run_repository.create_workflow_run("EMP_1")
    workflow_run_repository.create_agent_runs(
        workflow_run_id=workflow_run["workflow_run_id"],
        employee_id="EMP_1",
        agent_execution_history=[
            {
                "agent": "intake_agent",
                "status": "success",
                "summary": "Validated employee.",
            }
        ],
    )

    agent_runs = workflow_run_repository.get_agent_runs(
        workflow_run_id=workflow_run["workflow_run_id"].lower()
    )

    assert len(agent_runs) == 1
    assert agent_runs[0]["workflow_run_id"] == workflow_run["workflow_run_id"]


def test_knowledge_chunk_upsert_and_listing(memory_connection):
    first = knowledge_repository.upsert_knowledge_chunk(
        source="policies.md",
        title="Security Policy",
        content="Access requires approval.",
        content_hash="hash_1",
        embedding=[0.1, 0.2, 0.3],
    )
    second = knowledge_repository.upsert_knowledge_chunk(
        source="policies.md",
        title="Security Policy",
        content="Access requires manager approval.",
        content_hash="hash_1",
        embedding=[0.3, 0.2, 0.1],
    )

    chunks = knowledge_repository.list_knowledge_chunks()

    assert first["chunk_id"] == second["chunk_id"]
    assert len(chunks) == 1
    assert chunks[0]["content"] == "Access requires manager approval."
    assert chunks[0]["embedding"] == [0.3, 0.2, 0.1]
