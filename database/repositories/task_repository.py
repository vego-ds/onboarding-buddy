from datetime import UTC, datetime
from uuid import uuid4

from database.repositories.approval_repository import get_approval_by_task_id
from database.repositories.audit_repository import create_audit_log
from database.repositories.dependency_repository import get_dependencies_for_task
from database.db import get_connection

VALID_TASK_STATUSES = {"Pending", "In Progress", "Completed", "Blocked", "Failed"}


def create_task(employee_id, task):
    task_id = f"TASK_{uuid4().hex[:8].upper()}"
    now = datetime.now(UTC).isoformat()

    query = """
    INSERT INTO onboarding_tasks (
        task_id,
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
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    values = (
        task_id,
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
    query = "SELECT * FROM onboarding_tasks WHERE task_id = ?"

    with get_connection() as connection:
        row = connection.execute(query, (task_id,)).fetchone()

    if row is None:
        return None

    return dict(row)


def update_task_status(task_id, task_status):
    if task_status not in VALID_TASK_STATUSES:
        raise ValueError(f"Invalid task status: {task_status}")

    existing_task = get_task_by_id(task_id)

    if existing_task is None:
        return None

    if task_status == "In Progress":
        blockers = get_task_start_blockers(existing_task)
        if blockers:
            raise ValueError("Task cannot start yet: " + "; ".join(blockers))

    now = datetime.now(UTC).isoformat()
    query = """
    UPDATE onboarding_tasks
    SET task_status = ?, updated_at = ?
    WHERE task_id = ?
    """

    with get_connection() as connection:
        cursor = connection.execute(query, (task_status, now, task_id))
        connection.commit()

    if cursor.rowcount == 0:
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

    return updated_task


def get_task_start_blockers(task):
    blockers = []

    approval = get_approval_by_task_id(task["task_id"])
    if approval and approval.get("approval_status") != "Approved":
        blockers.append(
            f"approval is {approval.get('approval_status', 'not approved')}"
        )

    for dependency in get_dependencies_for_task(task["task_id"]):
        if dependency.get("depends_on_task_status") != "Completed":
            blockers.append(
                f"{dependency.get('depends_on_task_name')} is "
                f"{dependency.get('depends_on_task_status')}"
            )

    return blockers


def get_task_dependencies(task_id):
    return get_dependencies_for_task(task_id)
