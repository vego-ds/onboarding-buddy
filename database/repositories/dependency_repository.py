from datetime import UTC, datetime
from uuid import uuid4

from database.db import get_connection


def create_task_dependency(employee_id, task_id, depends_on_task_id):
    existing = get_dependency(task_id, depends_on_task_id)
    if existing:
        return existing

    dependency_id = f"DEPENDENCY_{uuid4().hex[:8].upper()}"
    now = datetime.now(UTC).isoformat()

    query = """
    INSERT INTO task_dependencies (
        dependency_id,
        employee_id,
        task_id,
        depends_on_task_id,
        created_at
    )
    VALUES (?, ?, ?, ?, ?)
    """

    values = (
        dependency_id,
        employee_id.upper(),
        task_id,
        depends_on_task_id,
        now,
    )

    with get_connection() as connection:
        connection.execute(query, values)
        connection.commit()

    return get_dependency_by_id(dependency_id)


def create_linear_task_dependencies(employee_id, tasks):
    dependencies = []

    for index, task in enumerate(tasks):
        if index == 0:
            continue

        dependencies.append(
            create_task_dependency(
                employee_id=employee_id,
                task_id=task["task_id"],
                depends_on_task_id=tasks[index - 1]["task_id"],
            )
        )

    return dependencies


def get_dependency(task_id, depends_on_task_id):
    query = """
    SELECT *
    FROM task_dependencies
    WHERE task_id = ? AND depends_on_task_id = ?
    """

    with get_connection() as connection:
        row = connection.execute(query, (task_id, depends_on_task_id)).fetchone()

    if row is None:
        return None

    return dict(row)


def get_dependency_by_id(dependency_id):
    query = "SELECT * FROM task_dependencies WHERE dependency_id = ?"

    with get_connection() as connection:
        row = connection.execute(query, (dependency_id,)).fetchone()

    if row is None:
        return None

    return dict(row)


def get_dependencies_for_task(task_id):
    query = """
    SELECT
        dependency.dependency_id,
        dependency.employee_id,
        dependency.task_id,
        dependency.depends_on_task_id,
        dependency.created_at,
        upstream.task_name AS depends_on_task_name,
        upstream.task_status AS depends_on_task_status
    FROM task_dependencies dependency
    JOIN onboarding_tasks upstream
        ON upstream.task_id = dependency.depends_on_task_id
    WHERE dependency.task_id = ?
    ORDER BY dependency.created_at ASC
    """

    with get_connection() as connection:
        rows = connection.execute(query, (task_id,)).fetchall()

    return [dict(row) for row in rows]


def get_downstream_tasks(task_id):
    query = """
    SELECT
        dependency.dependency_id,
        dependency.employee_id,
        dependency.task_id,
        dependency.depends_on_task_id,
        dependency.created_at,
        downstream.task_name,
        downstream.task_status,
        downstream.approval_required
    FROM task_dependencies dependency
    JOIN onboarding_tasks downstream
        ON downstream.task_id = dependency.task_id
    WHERE dependency.depends_on_task_id = ?
    ORDER BY dependency.created_at ASC
    """

    with get_connection() as connection:
        rows = connection.execute(query, (task_id,)).fetchall()

    return [dict(row) for row in rows]
