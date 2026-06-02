import sqlite3
from collections import Counter

from fastapi import APIRouter, HTTPException, Query

from backend.services_workflow import run_onboarding_workflow_for_employee
from database.repositories.employee_repository import (
    create_employee,
    get_employee_by_id,
    list_employees,
    update_employee,
)
from database.repositories.task_repository import get_tasks_by_employee_id
from schemas.employee import EmployeeCreateRequest, EmployeeUpdateRequest

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
    except sqlite3.IntegrityError as error:
        message = str(error)
        if "employees.employee_email" in message:
            raise HTTPException(
                status_code=409,
                detail="An employee with this email already exists.",
            )
        raise HTTPException(status_code=400, detail=message)
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.get("")
def get_employees(limit: int = Query(default=25, ge=1, le=100)):
    employees = list_employees(limit=limit)

    return {
        "employee_count": len(employees),
        "employees": employees,
    }


@router.get("/{employee_id}")
def get_employee(employee_id: str):
    employee = get_employee_by_id(employee_id)

    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found.")

    return employee


@router.put("/{employee_id}")
def update_employee_record(employee_id: str, employee: EmployeeUpdateRequest):
    try:
        updated_employee = update_employee(employee_id, employee)

        if updated_employee is None:
            raise HTTPException(status_code=404, detail="Employee not found.")

        return {
            "employee_id": updated_employee["employee_id"],
            "status": "updated",
            "message": "Employee onboarding record updated successfully.",
            "employee": updated_employee,
        }
    except sqlite3.IntegrityError as error:
        message = str(error)
        if "employees.employee_email" in message:
            raise HTTPException(
                status_code=409,
                detail="An employee with this email already exists.",
            )
        raise HTTPException(status_code=400, detail=message)


@router.get("/{employee_id}/tasks")
def get_employee_tasks(employee_id: str):
    employee = get_employee_by_id(employee_id)

    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found.")

    tasks = get_tasks_by_employee_id(employee_id)
    status_counts = Counter(task.get("task_status", "Unknown") for task in tasks)
    priority_counts = Counter(task.get("task_priority", "Unspecified") for task in tasks)
    approval_required_count = sum(1 for task in tasks if task.get("approval_required"))

    return {
        "employee_id": employee["employee_id"],
        "employee": employee,
        "task_count": len(tasks),
        "status_counts": dict(status_counts),
        "priority_counts": dict(priority_counts),
        "approval_required_count": approval_required_count,
        "tasks": tasks,
    }


@router.post("/{employee_id}/generate-onboarding-plan")
def generate_onboarding_plan(employee_id: str):
    final_state = run_onboarding_workflow_for_employee(employee_id)

    if final_state is None:
        raise HTTPException(status_code=404, detail="Employee not found.")

    tasks = final_state.get("onboarding_tasks", [])
    status_counts = Counter(task.get("task_status", "Unknown") for task in tasks)
    approval_required_count = sum(1 for task in tasks if task.get("approval_required"))

    return {
        "employee_id": employee_id.upper(),
        "workflow_status": final_state.get("workflow_status"),
        "next_agent": final_state.get("next_agent"),
        "routing_reason": final_state.get("supervisor_routing_reason"),
        "agent_outputs": final_state.get("agent_outputs"),
        "task_count": len(tasks),
        "status_counts": dict(status_counts),
        "approval_required_count": approval_required_count,
        "tasks": tasks,
    }
