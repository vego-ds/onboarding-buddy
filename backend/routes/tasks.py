from fastapi import APIRouter, HTTPException

from database.repositories.task_repository import (
    get_task_dependencies,
    get_task_by_id,
    update_task_status,
)
from schemas.task import TaskStatusUpdateRequest

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("/{task_id}")
def get_task(task_id: str):
    task = get_task_by_id(task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found.")

    return task


@router.get("/{task_id}/dependencies")
def get_dependencies(task_id: str):
    task = get_task_by_id(task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found.")

    dependencies = get_task_dependencies(task_id)

    return {
        "task_id": task_id,
        "dependency_count": len(dependencies),
        "dependencies": dependencies,
    }


@router.patch("/{task_id}/status")
def update_status(task_id: str, status_update: TaskStatusUpdateRequest):
    try:
        task = update_task_status(task_id, status_update.task_status)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found.")

    return {
        "task_id": task["task_id"],
        "status": "updated",
        "message": "Task status updated successfully.",
        "task": task,
    }
