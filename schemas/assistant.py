from pydantic import BaseModel


class AssistantChatRequest(BaseModel):
    question: str
    employee_id: str | None = None
