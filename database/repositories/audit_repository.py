from datetime import UTC, datetime
from uuid import uuid4

from database.db import get_connection
from database.repositories.employee_repository import get_employee_by_id


def create_audit_log(
    event_type,
    event_message,
    employee_id=None,
    workflow_run_id=None,
    agent_name=None,
    routing_reason=None,
    event_status="Success",
):
    log_id = f"LOG_{uuid4().hex[:8].upper()}"
    now = datetime.now(UTC).isoformat()
    employee = get_employee_by_id(employee_id) if employee_id else None
    tenant_id = employee.get("tenant_id", "TENANT_DEFAULT") if employee else "TENANT_DEFAULT"

    query = """
    INSERT INTO audit_logs (
        log_id,
        tenant_id,
        employee_id,
        workflow_run_id,
        event_type,
        event_message,
        agent_name,
        routing_reason,
        event_status,
        timestamp
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    values = (
        log_id,
        tenant_id,
        employee_id.upper() if employee_id else None,
        workflow_run_id,
        event_type,
        event_message,
        agent_name,
        routing_reason,
        event_status,
        now,
    )

    with get_connection() as connection:
        connection.execute(query, values)
        connection.commit()

    return get_audit_log_by_id(log_id)


def get_audit_log_by_id(log_id):
    query = "SELECT * FROM audit_logs WHERE log_id = ?"

    with get_connection() as connection:
        row = connection.execute(query, (log_id,)).fetchone()

    if row is None:
        return None

    return dict(row)


def get_audit_logs(employee_id=None, limit=50):
    if employee_id:
        query = """
        SELECT *
        FROM audit_logs
        WHERE employee_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
        """
        values = (employee_id.upper(), limit)
    else:
        query = """
        SELECT *
        FROM audit_logs
        ORDER BY timestamp DESC
        LIMIT ?
        """
        values = (limit,)

    with get_connection() as connection:
        rows = connection.execute(query, values).fetchall()

    return [dict(row) for row in rows]
