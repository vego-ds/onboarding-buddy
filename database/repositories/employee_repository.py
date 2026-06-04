from datetime import UTC, datetime
from uuid import uuid4

from database.db import get_connection


def create_employee(employee_data, tenant_id="TENANT_DEFAULT"):
    employee_id = f"EMP_{uuid4().hex[:8].upper()}"
    now = datetime.now(UTC).isoformat()

    query = """
    INSERT INTO employees (
        employee_id,
        tenant_id,
        employee_name,
        employee_email,
        role,
        department,
        joining_date,
        onboarding_status,
        created_at,
        updated_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    values = (
        employee_id,
        tenant_id,
        employee_data.employee_name,
        employee_data.employee_email,
        employee_data.role,
        employee_data.department,
        employee_data.joining_date,
        "PENDING",
        now,
        now,
    )

    with get_connection() as connection:
        connection.execute(query, values)
        connection.commit()

    return get_employee_by_id(employee_id)


def get_employee_by_id(employee_id):
    query = "SELECT * FROM employees WHERE employee_id = ?"

    with get_connection() as connection:
        employee = connection.execute(query, (employee_id.upper(),)).fetchone()

    if employee is None:
        return None

    return dict(employee)


def list_employees(limit=25, tenant_id=None):
    where_clause = "WHERE tenant_id = ?" if tenant_id else ""
    values = (tenant_id, limit) if tenant_id else (limit,)
    query = """
    SELECT
        employee_id,
        tenant_id,
        employee_name,
        employee_email,
        role,
        department,
        joining_date,
        onboarding_status,
        created_at,
        updated_at
    FROM employees
    {where_clause}
    ORDER BY created_at DESC
    LIMIT ?
    """.format(where_clause=where_clause)

    with get_connection() as connection:
        rows = connection.execute(query, values).fetchall()

    return [dict(row) for row in rows]


def update_employee_status(employee_id, onboarding_status):
    now = datetime.now(UTC).isoformat()
    query = """
    UPDATE employees
    SET onboarding_status = ?, updated_at = ?
    WHERE employee_id = ?
    """

    with get_connection() as connection:
        connection.execute(query, (onboarding_status, now, employee_id.upper()))
        connection.commit()

    return get_employee_by_id(employee_id)


def update_employee(employee_id, employee_data):
    now = datetime.now(UTC).isoformat()
    query = """
    UPDATE employees
    SET
        employee_name = ?,
        employee_email = ?,
        role = ?,
        department = ?,
        joining_date = ?,
        updated_at = ?
    WHERE employee_id = ?
    """

    values = (
        employee_data.employee_name,
        employee_data.employee_email,
        employee_data.role,
        employee_data.department,
        employee_data.joining_date,
        now,
        employee_id.upper(),
    )

    with get_connection() as connection:
        cursor = connection.execute(query, values)
        connection.commit()

    if cursor.rowcount == 0:
        return None

    return get_employee_by_id(employee_id)
