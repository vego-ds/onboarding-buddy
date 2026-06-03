from datetime import UTC, datetime
from uuid import uuid4

from database.repositories.audit_repository import create_audit_log
from database.db import get_connection

PENDING_APPROVAL = "Awaiting Approval"
VALID_APPROVAL_STATUSES = {
    "Awaiting Approval",
    "Approved",
    "Rejected",
    "Revision Requested",
}


def create_approval(employee_id, related_task_id, action_type):
    approval_id = f"APPROVAL_{uuid4().hex[:8].upper()}"
    now = datetime.now(UTC).isoformat()

    query = """
    INSERT INTO approvals (
        approval_id,
        employee_id,
        related_task_id,
        action_type,
        approval_status,
        created_at
    )
    VALUES (?, ?, ?, ?, ?, ?)
    """

    values = (
        approval_id,
        employee_id.upper(),
        related_task_id,
        action_type,
        PENDING_APPROVAL,
        now,
    )

    with get_connection() as connection:
        connection.execute(query, values)
        connection.commit()

    approval = get_approval_by_id(approval_id)
    create_audit_log(
        employee_id=employee_id,
        event_type="approval_created",
        event_message=f"Approval created for {action_type}.",
    )

    return approval


def create_task_approvals(employee_id, tasks):
    approvals = []

    for task in tasks:
        if task.get("approval_required") and not get_approval_by_task_id(task["task_id"]):
            approvals.append(
                create_approval(
                    employee_id=employee_id,
                    related_task_id=task["task_id"],
                    action_type=f"Review task: {task['task_name']}",
                )
            )

    return approvals


def get_approval_by_task_id(task_id):
    query = "SELECT * FROM approvals WHERE related_task_id = ?"

    with get_connection() as connection:
        row = connection.execute(query, (task_id,)).fetchone()

    if row is None:
        return None

    return dict(row)


def get_approval_by_id(approval_id):
    query = "SELECT * FROM approvals WHERE approval_id = ?"

    with get_connection() as connection:
        row = connection.execute(query, (approval_id,)).fetchone()

    if row is None:
        return None

    return dict(row)


def get_approvals(employee_id=None, approval_status=None):
    filters = []
    values = []

    if employee_id:
        filters.append("employee_id = ?")
        values.append(employee_id.upper())

    if approval_status:
        filters.append("approval_status = ?")
        values.append(approval_status)

    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
    query = f"""
    SELECT *
    FROM approvals
    {where_clause}
    ORDER BY created_at DESC
    """

    with get_connection() as connection:
        rows = connection.execute(query, values).fetchall()

    return [dict(row) for row in rows]


def update_approval_decision(
    approval_id,
    approval_status,
    review_notes="",
    reviewed_by="HR",
):
    if approval_status not in VALID_APPROVAL_STATUSES:
        raise ValueError(f"Invalid approval status: {approval_status}")

    now = datetime.now(UTC).isoformat()
    query = """
    UPDATE approvals
    SET
        approval_status = ?,
        review_notes = ?,
        reviewed_by = ?,
        reviewed_at = ?
    WHERE approval_id = ?
    """

    with get_connection() as connection:
        cursor = connection.execute(
            query,
            (
                approval_status,
                review_notes,
                reviewed_by,
                now,
                approval_id,
            ),
        )
        connection.commit()

    if cursor.rowcount == 0:
        return None

    approval = get_approval_by_id(approval_id)
    create_audit_log(
        employee_id=approval["employee_id"],
        event_type="approval_decision",
        event_message=(
            f"Approval {approval_id} marked {approval_status} by {reviewed_by}."
        ),
    )

    if approval_status == "Approved" and approval.get("related_task_id"):
        from database.repositories.task_repository import refresh_task_lock_state

        refresh_task_lock_state(
            approval["related_task_id"],
            trigger="approval decision",
        )

    return approval
