from datetime import datetime
from uuid import uuid4

from database.db import get_connection


def create_task(employee_id, task):
    task_id = f"TASK_{uuid4().hex[:8].upper()}"
    now = datetime.utcnow().isoformat()

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
