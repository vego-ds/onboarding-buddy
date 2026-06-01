from fastapi import APIRouter, HTTPException

from database.repositories.employee_repository import (
    create_employee,
    get_employee_by_id,
)
from database.repositories.task_repository import get_tasks_by_employee_id
from schemas.employee import EmployeeCreateRequest

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.post("")
def create_employee_record(employee: EmployeeCreateRequest):
    try:
        created_employee = create_employee(employee)
        return {
            "employee_id": created_employee["employee_id"],
            "status": "created",
            "message": "Employee onboarding record created successfully.",
            "employee": created_employee,
        }
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.get("/{employee_id}")
def get_employee(employee_id: str):
    employee = get_employee_by_id(employee_id)

    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found.")

    return employee


@router.get("/{employee_id}/tasks")
def get_employee_tasks(employee_id: str):
    employee = get_employee_by_id(employee_id)

    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found.")

    tasks = get_tasks_by_employee_id(employee_id)

    return {
        "employee_id": employee_id,
        "task_count": len(tasks),
        "tasks": tasks,
    }
