from datetime import UTC, datetime
from uuid import uuid4

from database.db import get_connection


def create_refresh_token(user_id, token_hash, expires_at):
    refresh_token_id = f"REFRESH_{uuid4().hex[:12].upper()}"
    now = datetime.now(UTC).isoformat()
    query = """
    INSERT INTO refresh_tokens (
        refresh_token_id,
        user_id,
        token_hash,
        expires_at,
        created_at
    )
    VALUES (?, ?, ?, ?, ?)
    """

    with get_connection() as connection:
        connection.execute(
            query,
            (refresh_token_id, user_id, token_hash, expires_at, now),
        )
        connection.commit()

    return get_refresh_token_by_hash(token_hash)


def get_refresh_token_by_hash(token_hash):
    query = "SELECT * FROM refresh_tokens WHERE token_hash = ?"

    with get_connection() as connection:
        row = connection.execute(query, (token_hash,)).fetchone()

    if row is None:
        return None

    return dict(row)


def revoke_refresh_token(token_hash):
    now = datetime.now(UTC).isoformat()
    query = """
    UPDATE refresh_tokens
    SET revoked_at = ?
    WHERE token_hash = ?
    """

    with get_connection() as connection:
        cursor = connection.execute(query, (now, token_hash))
        connection.commit()

    return cursor.rowcount


def create_password_reset_token(user_id, token_hash, expires_at):
    reset_token_id = f"RESET_{uuid4().hex[:12].upper()}"
    now = datetime.now(UTC).isoformat()
    query = """
    INSERT INTO password_reset_tokens (
        reset_token_id,
        user_id,
        token_hash,
        expires_at,
        created_at
    )
    VALUES (?, ?, ?, ?, ?)
    """

    with get_connection() as connection:
        connection.execute(
            query,
            (reset_token_id, user_id, token_hash, expires_at, now),
        )
        connection.commit()

    return get_password_reset_token_by_hash(token_hash)


def get_password_reset_token_by_hash(token_hash):
    query = "SELECT * FROM password_reset_tokens WHERE token_hash = ?"

    with get_connection() as connection:
        row = connection.execute(query, (token_hash,)).fetchone()

    if row is None:
        return None

    return dict(row)


def mark_password_reset_token_used(token_hash):
    now = datetime.now(UTC).isoformat()
    query = """
    UPDATE password_reset_tokens
    SET used_at = ?
    WHERE token_hash = ?
    """

    with get_connection() as connection:
        cursor = connection.execute(query, (now, token_hash))
        connection.commit()

    return cursor.rowcount


def create_auth_audit_log(
    event_type,
    event_status,
    event_message,
    tenant_id=None,
    user_id=None,
    email=None,
    ip_address=None,
    user_agent=None,
):
    auth_audit_id = f"AUTH_AUDIT_{uuid4().hex[:12].upper()}"
    now = datetime.now(UTC).isoformat()
    query = """
    INSERT INTO auth_audit_logs (
        auth_audit_id,
        tenant_id,
        user_id,
        email,
        event_type,
        event_status,
        event_message,
        ip_address,
        user_agent,
        created_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    with get_connection() as connection:
        connection.execute(
            query,
            (
                auth_audit_id,
                tenant_id,
                user_id,
                email,
                event_type,
                event_status,
                event_message,
                ip_address,
                user_agent,
                now,
            ),
        )
        connection.commit()

    return {"auth_audit_id": auth_audit_id, "created_at": now}
