from fastapi import APIRouter, Depends, HTTPException

from backend.security.auth import assert_employee_access, get_current_user, require_roles
from backend.services.assistant_service import (
    answer_onboarding_question,
    sync_knowledge_index,
)
from schemas.assistant import AssistantChatRequest

router = APIRouter(prefix="/assistant", tags=["Assistant"])


@router.post("/chat")
def chat_with_assistant(
    request: AssistantChatRequest,
    current_user=Depends(get_current_user),
):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question is required.")
    if request.employee_id:
        assert_employee_access(current_user, request.employee_id)

    return answer_onboarding_question(
        question=request.question.strip(),
        user_role=current_user["role"],
        employee_id=request.employee_id,
        current_user=current_user,
    )


@router.post("/knowledge/reindex")
def reindex_assistant_knowledge(
    current_user=Depends(require_roles("hr_admin", "admin")),
):
    try:
        return sync_knowledge_index()
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Knowledge reindex failed: {error}",
        ) from error
