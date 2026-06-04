from fastapi import APIRouter, HTTPException

from backend.services.assistant_service import (
    answer_onboarding_question,
    sync_knowledge_index,
)
from schemas.assistant import AssistantChatRequest

router = APIRouter(prefix="/assistant", tags=["Assistant"])


@router.post("/chat")
def chat_with_assistant(request: AssistantChatRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question is required.")

    return answer_onboarding_question(
        question=request.question.strip(),
        user_role=request.user_role,
        employee_id=request.employee_id,
    )


@router.post("/knowledge/reindex")
def reindex_assistant_knowledge():
    try:
        return sync_knowledge_index()
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Knowledge reindex failed: {error}",
        ) from error
