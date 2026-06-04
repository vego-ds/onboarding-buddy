from fastapi import APIRouter, Depends, HTTPException

from backend.security.auth import assert_employee_access, get_current_user
from database.repositories.task_repository import (
    get_task_dependencies,
    get_task_by_id,
    get_task_enforcement_state,
    update_task_status,
)
from schemas.task import TaskStatusUpdateRequest

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("/{task_id}")
def get_task(task_id: str, current_user=Depends(get_current_user)):
    task = get_task_by_id(task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found.")
    assert_employee_access(current_user, task["employee_id"])

    return {
        "task": task,
        "enforcement": get_task_enforcement_state(task),
    }


@router.get("/{task_id}/dependencies")
def get_dependencies(task_id: str, current_user=Depends(get_current_user)):
    task = get_task_by_id(task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found.")
    assert_employee_access(current_user, task["employee_id"])

    dependencies = get_task_dependencies(task_id)
    enforcement = get_task_enforcement_state(task)

    return {
        "task_id": task["task_id"],
        "dependency_count": len(dependencies),
        "dependencies": dependencies,
        "enforcement": enforcement,
        "is_locked": enforcement["is_locked"],
        "can_start": enforcement["can_start"],
        "lock_reasons": enforcement["lock_reasons"],
    }


@router.patch("/{task_id}/status")
def update_status(
    task_id: str,
    status_update: TaskStatusUpdateRequest,
    current_user=Depends(get_current_user),
):
    if current_user["role"] not in {"manager", "hr_admin", "admin"}:
        raise HTTPException(status_code=403, detail="Insufficient permissions.")
    existing_task = get_task_by_id(task_id)
    if existing_task is None:
        raise HTTPException(status_code=404, detail="Task not found.")
    assert_employee_access(current_user, existing_task["employee_id"])
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
        "enforcement": get_task_enforcement_state(task),
    }
