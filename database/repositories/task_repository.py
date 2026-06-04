from datetime import UTC, datetime
from uuid import uuid4

from database.repositories.approval_repository import get_approval_by_task_id
from database.repositories.audit_repository import create_audit_log
from database.repositories.dependency_repository import (
    get_dependencies_for_task,
    get_downstream_tasks,
)
from database.repositories.employee_repository import get_employee_by_id
from database.db import get_connection

VALID_TASK_STATUSES = {"Pending", "In Progress", "Completed", "Blocked", "Failed"}


def normalize_task_id(task_id):
    return task_id.strip().upper()


def create_task(employee_id, task):
    task_id = f"TASK_{uuid4().hex[:8].upper()}"
    now = datetime.now(UTC).isoformat()
    employee = get_employee_by_id(employee_id)
    tenant_id = employee.get("tenant_id", "TENANT_DEFAULT") if employee else "TENANT_DEFAULT"

    query = """
    INSERT INTO onboarding_tasks (
        task_id,
        tenant_id,
        employee_id,
        task_name,
        task_description,
        task_status,
        task_priority,
        approval_required,
        generated_by_agent,
        assigned_owner,
        created_at,
        updated_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    values = (
        task_id,
        tenant_id,
        employee_id,
        task["task_name"],
        task.get("task_description", ""),
        task.get("task_status", "Pending"),
        task.get("task_priority", "Medium"),
        1 if task.get("approval_required") else 0,
        task.get("generated_by_agent", "task_planning_agent"),
        task.get("assigned_owner", "HR"),
        now,
        now,
    )

    with get_connection() as connection:
        connection.execute(query, values)
        connection.commit()

    return {
        "task_id": task_id,
        **task,
    }


def create_tasks(employee_id, tasks):
    saved_tasks = []

    for task in tasks:
        saved_task = create_task(employee_id, task)
        saved_tasks.append(saved_task)

    return saved_tasks


def get_tasks_by_employee_id(employee_id):
    query = """
    SELECT * FROM onboarding_tasks
    WHERE employee_id = ?
    ORDER BY created_at ASC
    """

    with get_connection() as connection:
        rows = connection.execute(query, (employee_id.upper(),)).fetchall()

    return [dict(row) for row in rows]


def get_task_by_id(task_id):
    task_id = normalize_task_id(task_id)
    query = "SELECT * FROM onboarding_tasks WHERE task_id = ?"

    with get_connection() as connection:
        row = connection.execute(query, (task_id,)).fetchone()

    if row is None:
        return None

    return dict(row)


def set_task_status(task_id, task_status):
    task_id = normalize_task_id(task_id)
    now = datetime.now(UTC).isoformat()
    query = """
    UPDATE onboarding_tasks
    SET task_status = ?, updated_at = ?
    WHERE task_id = ?
    """

    with get_connection() as connection:
        cursor = connection.execute(query, (task_status, now, task_id))
        connection.commit()

    return cursor.rowcount


def update_task_status(task_id, task_status):
    task_id = normalize_task_id(task_id)
    if task_status not in VALID_TASK_STATUSES:
        raise ValueError(f"Invalid task status: {task_status}")

    existing_task = get_task_by_id(task_id)

    if existing_task is None:
        return None

    if task_status == "In Progress":
        enforcement = get_task_enforcement_state(existing_task)
        if enforcement["is_locked"]:
            if existing_task.get("task_status") != "Blocked":
                set_task_status(task_id, "Blocked")
            create_audit_log(
                employee_id=existing_task["employee_id"],
                event_type="task_start_blocked",
                event_message=(
                    f"Task {existing_task['task_name']} could not start: "
                    f"{'; '.join(enforcement['lock_reasons'])}."
                ),
                event_status="Blocked",
            )
            raise ValueError(
                "Task cannot start yet: " + "; ".join(enforcement["lock_reasons"])
            )

    if set_task_status(task_id, task_status) == 0:
        return None

    updated_task = get_task_by_id(task_id)
    create_audit_log(
        employee_id=updated_task["employee_id"],
        event_type="task_status_updated",
        event_message=(
            f"Task {updated_task['task_name']} changed from "
            f"{existing_task['task_status']} to {task_status}."
        ),
    )

    if task_status == "Completed":
        refresh_downstream_task_locks(task_id)

    return updated_task


def get_task_start_blockers(task):
    return get_task_enforcement_state(task)["lock_reasons"]


def get_task_enforcement_state(task):
    if isinstance(task, str):
        task = get_task_by_id(task)

    if task is None:
        return None

    lock_reasons = []
    approval = get_approval_by_task_id(task["task_id"])
    approval_status = approval.get("approval_status") if approval else None

    if task.get("approval_required") and approval is None:
        lock_reasons.append("approval record is missing")
    elif approval and approval.get("approval_status") != "Approved":
        lock_reasons.append(
            f"approval is {approval.get('approval_status', 'not approved')}"
        )

    dependencies = get_dependencies_for_task(task["task_id"])
    blocked_dependencies = []
    for dependency in dependencies:
        if dependency.get("depends_on_task_status") != "Completed":
            blocked_dependencies.append(dependency)
            lock_reasons.append(
                f"{dependency.get('depends_on_task_name')} is "
                f"{dependency.get('depends_on_task_status')}"
            )

    return {
        "task_id": task["task_id"],
        "task_status": task.get("task_status"),
        "is_locked": bool(lock_reasons),
        "can_start": not lock_reasons,
        "lock_reasons": lock_reasons,
        "approval_status": approval_status,
        "dependency_count": len(dependencies),
        "blocked_dependency_count": len(blocked_dependencies),
        "dependencies": dependencies,
    }


def refresh_task_lock_state(task_id, trigger="dependency_updated"):
    task_id = normalize_task_id(task_id)
    task = get_task_by_id(task_id)
    if task is None:
        return None

    enforcement = get_task_enforcement_state(task)

    if task.get("task_status") == "Blocked" and not enforcement["is_locked"]:
        set_task_status(task_id, "Pending")
        create_audit_log(
            employee_id=task["employee_id"],
            event_type="task_unlocked",
            event_message=(
                f"Task {task['task_name']} was unlocked after {trigger}."
            ),
        )
        return get_task_by_id(task_id)

    if enforcement["is_locked"]:
        create_audit_log(
            employee_id=task["employee_id"],
            event_type="task_still_locked",
            event_message=(
                f"Task {task['task_name']} remains locked: "
                f"{'; '.join(enforcement['lock_reasons'])}."
            ),
            event_status="Blocked",
        )

    return task


def refresh_downstream_task_locks(completed_task_id):
    completed_task_id = normalize_task_id(completed_task_id)
    refreshed_tasks = []

    for downstream in get_downstream_tasks(completed_task_id):
        refreshed = refresh_task_lock_state(
            downstream["task_id"],
            trigger="upstream task completion",
        )
        if refreshed:
            refreshed_tasks.append(refreshed)

    return refreshed_tasks


def get_task_dependencies(task_id):
    return get_dependencies_for_task(normalize_task_id(task_id))
