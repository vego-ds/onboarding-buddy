from pydantic import BaseModel


class AssistantChatRequest(BaseModel):
    question: str
    user_role: str = "Employee"
    employee_id: str | None = None

