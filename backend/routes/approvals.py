from fastapi import APIRouter, Depends, HTTPException, Query

from backend.security.auth import require_roles
from database.repositories.approval_repository import (
    get_approval_by_id,
    get_approvals,
    update_approval_decision,
)
from schemas.approval import ApprovalDecisionRequest

router = APIRouter(prefix="/approvals", tags=["Approvals"])


@router.get("")
def list_approvals(
    employee_id: str | None = None,
    approval_status: str | None = Query(default=None),
    current_user=Depends(require_roles("hr_admin", "admin")),
):
    approvals = get_approvals(
        employee_id=employee_id,
        approval_status=approval_status,
        tenant_id=current_user.get("tenant_id", "TENANT_DEFAULT"),
    )

    return {
        "approval_count": len(approvals),
        "approvals": approvals,
    }


@router.get("/{approval_id}")
def get_approval(
    approval_id: str,
    current_user=Depends(require_roles("hr_admin", "admin")),
):
    approval = get_approval_by_id(approval_id)

    if approval is None:
        raise HTTPException(status_code=404, detail="Approval not found.")

    return approval


@router.patch("/{approval_id}")
def submit_approval_decision(
    approval_id: str,
    decision: ApprovalDecisionRequest,
    current_user=Depends(require_roles("hr_admin", "admin")),
):
    try:
        approval = update_approval_decision(
            approval_id=approval_id,
            approval_status=decision.approval_status,
            review_notes=decision.review_notes,
            reviewed_by=decision.reviewed_by,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    if approval is None:
        raise HTTPException(status_code=404, detail="Approval not found.")

    return {
        "approval_id": approval["approval_id"],
        "status": "updated",
        "message": "Approval decision saved successfully.",
        "approval": approval,
    }
