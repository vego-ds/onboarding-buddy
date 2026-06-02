from pydantic import BaseModel


class ApprovalDecisionRequest(BaseModel):
    approval_status: str
    review_notes: str = ""
    reviewed_by: str = "HR"
