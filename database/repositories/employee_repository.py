from datetime import datetime
from uuid import uuid4

from database.db import get_connection


def create_employee(employee_data):
    employee_id = f"EMP_{uuid4().hex[:8].upper()}"
    now = datetime.utcnow().isoformat()

    query = """
    INSERT INTO employees (
        employee_id,
        employee_name,
        employee_email,
        role,
        department,
        joining_date,
        onboarding_status,
        created_at,
        updated_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    values = (
        employee_id,
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


def list_employees(limit=25):
    query = """
    SELECT
        employee_id,
        employee_name,
        employee_email,
        role,
        department,
        joining_date,
        onboarding_status,
        created_at,
        updated_at
    FROM employees
    ORDER BY created_at DESC
    LIMIT ?
    """

    with get_connection() as connection:
        rows = connection.execute(query, (limit,)).fetchall()

    return [dict(row) for row in rows]


def update_employee_status(employee_id, onboarding_status):
    now = datetime.utcnow().isoformat()
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
    now = datetime.utcnow().isoformat()
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
