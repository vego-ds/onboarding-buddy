from datetime import UTC, datetime
from uuid import uuid4

from database.db import get_connection


def create_workflow_run(employee_id):
    workflow_run_id = f"WF_{uuid4().hex[:8].upper()}"
    now = datetime.now(UTC).isoformat()

    query = """
    INSERT INTO workflow_runs (
        workflow_run_id,
        employee_id,
        workflow_status,
        started_at
    )
    VALUES (?, ?, ?, ?)
    """

    with get_connection() as connection:
        connection.execute(
            query,
            (
                workflow_run_id,
                employee_id.upper(),
                "Running",
                now,
            ),
        )
        connection.commit()

    return get_workflow_run_by_id(workflow_run_id)


def complete_workflow_run(workflow_run_id, final_state):
    now = datetime.now(UTC).isoformat()
    query = """
    UPDATE workflow_runs
    SET
        workflow_status = ?,
        current_agent = ?,
        next_agent = ?,
        failure_reason = ?,
        completed_at = ?
    WHERE workflow_run_id = ?
    """

    with get_connection() as connection:
        connection.execute(
            query,
            (
                final_state.get("workflow_status", "Completed"),
                final_state.get("current_agent"),
                final_state.get("next_agent"),
                final_state.get("failure_reason"),
                now,
                workflow_run_id,
            ),
        )
        connection.commit()

    return get_workflow_run_by_id(workflow_run_id)


def create_agent_runs(workflow_run_id, employee_id, agent_execution_history):
    saved_runs = []

    for index, execution in enumerate(agent_execution_history, start=1):
        saved_runs.append(
            create_agent_run(
                workflow_run_id=workflow_run_id,
                employee_id=employee_id,
                agent_name=execution.get("agent", "unknown_agent"),
                agent_role=execution.get("agent", "unknown_agent"),
                execution_order=index,
                output_summary=execution.get("summary", ""),
                execution_status=execution.get("status", "success").title(),
            )
        )

    return saved_runs


def create_agent_run(
    workflow_run_id,
    employee_id,
    agent_name,
    agent_role,
    execution_order,
    output_summary,
    execution_status,
):
    agent_run_id = f"AGENT_RUN_{uuid4().hex[:8].upper()}"
    now = datetime.now(UTC).isoformat()

    query = """
    INSERT INTO agent_runs (
        agent_run_id,
        workflow_run_id,
        employee_id,
        agent_name,
        agent_role,
        execution_order,
        output_summary,
        execution_status,
        started_at,
        completed_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    values = (
        agent_run_id,
        workflow_run_id,
        employee_id.upper(),
        agent_name,
        agent_role,
        execution_order,
        output_summary,
        execution_status,
        now,
        now,
    )

    with get_connection() as connection:
        connection.execute(query, values)
        connection.commit()

    return get_agent_run_by_id(agent_run_id)


def get_workflow_run_by_id(workflow_run_id):
    query = "SELECT * FROM workflow_runs WHERE workflow_run_id = ?"

    with get_connection() as connection:
        row = connection.execute(query, (workflow_run_id,)).fetchone()

    if row is None:
        return None

    return dict(row)


def get_workflow_runs(employee_id=None, limit=25):
    if employee_id:
        query = """
        SELECT *
        FROM workflow_runs
        WHERE employee_id = ?
        ORDER BY started_at DESC
        LIMIT ?
        """
        values = (employee_id.upper(), limit)
    else:
        query = """
        SELECT *
        FROM workflow_runs
        ORDER BY started_at DESC
        LIMIT ?
        """
        values = (limit,)

    with get_connection() as connection:
        rows = connection.execute(query, values).fetchall()

    return [dict(row) for row in rows]


def get_agent_run_by_id(agent_run_id):
    query = "SELECT * FROM agent_runs WHERE agent_run_id = ?"

    with get_connection() as connection:
        row = connection.execute(query, (agent_run_id,)).fetchone()

    if row is None:
        return None

    return dict(row)


def get_agent_runs(workflow_run_id=None, employee_id=None):
    filters = []
    values = []

    if workflow_run_id:
        filters.append("workflow_run_id = ?")
        values.append(workflow_run_id)

    if employee_id:
        filters.append("employee_id = ?")
        values.append(employee_id.upper())

    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
    query = f"""
    SELECT *
    FROM agent_runs
    {where_clause}
    ORDER BY execution_order ASC, started_at ASC
    """

    with get_connection() as connection:
        rows = connection.execute(query, values).fetchall()

    return [dict(row) for row in rows]
