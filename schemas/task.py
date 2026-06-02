from pydantic import BaseModel


class TaskStatusUpdateRequest(BaseModel):
    task_status: str
