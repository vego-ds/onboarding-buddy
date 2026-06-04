from datetime import UTC, datetime
from uuid import uuid4

from database.db import get_connection

VALID_USER_ROLES = {"employee", "manager", "hr_admin", "admin"}


def normalize_user_id(user_id):
    return str(user_id or "").strip().upper()


def normalize_email(email):
    return str(email or "").strip().lower()


def normalize_employee_id(employee_id):
    if not employee_id:
        return None
    return str(employee_id).strip().upper()


def create_user(
    name,
    email,
    password_hash,
    role,
    employee_id=None,
    manager_id=None,
):
    role = str(role or "").strip().lower()
    if role not in VALID_USER_ROLES:
        raise ValueError(f"Invalid user role: {role}")

    user_id = f"USER_{uuid4().hex[:8].upper()}"
    now = datetime.now(UTC).isoformat()
    query = """
    INSERT INTO users (
        user_id,
        name,
        email,
        password_hash,
        role,
        employee_id,
        manager_id,
        created_at,
        updated_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    with get_connection() as connection:
        connection.execute(
            query,
            (
                user_id,
                name,
                normalize_email(email),
                password_hash,
                role,
                normalize_employee_id(employee_id),
                normalize_user_id(manager_id) if manager_id else None,
                now,
                now,
            ),
        )
        connection.commit()

    return get_user_by_id(user_id)


def get_user_by_id(user_id):
    query = "SELECT * FROM users WHERE user_id = ?"

    with get_connection() as connection:
        row = connection.execute(query, (normalize_user_id(user_id),)).fetchone()

    if row is None:
        return None

    return dict(row)


def get_user_by_email(email):
    query = "SELECT * FROM users WHERE email = ?"

    with get_connection() as connection:
        row = connection.execute(query, (normalize_email(email),)).fetchone()

    if row is None:
        return None

    return dict(row)


def get_user_by_employee_id(employee_id):
    query = "SELECT * FROM users WHERE employee_id = ?"

    with get_connection() as connection:
        row = connection.execute(query, (normalize_employee_id(employee_id),)).fetchone()

    if row is None:
        return None

    return dict(row)


def list_users_by_manager_id(manager_id):
    query = """
    SELECT *
    FROM users
    WHERE manager_id = ?
    ORDER BY created_at ASC
    """

    with get_connection() as connection:
        rows = connection.execute(
            query,
            (normalize_user_id(manager_id),),
        ).fetchall()

    return [dict(row) for row in rows]


def sanitize_user(user):
    if user is None:
        return None

    sanitized = dict(user)
    sanitized.pop("password_hash", None)
    return sanitized
