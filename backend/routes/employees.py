from collections import Counter

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.security.auth import (
    assert_employee_access,
    get_current_user,
    is_hr_or_admin,
    require_roles,
)
from backend.services_workflow import run_onboarding_workflow_for_employee
from database.db import get_integrity_error_classes, is_duplicate_email_error
from database.repositories.employee_repository import (
    create_employee,
    get_employee_by_id,
    list_employees,
    update_employee,
)
from database.repositories.approval_repository import get_approvals
from database.repositories.audit_repository import create_audit_log, get_audit_logs
from database.repositories.task_repository import get_tasks_by_employee_id
from database.repositories.user_repository import list_users_by_manager_id
from schemas.employee import EmployeeCreateRequest, EmployeeUpdateRequest

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.post("")
def create_employee_record(
    employee: EmployeeCreateRequest,
    current_user=Depends(require_roles("hr_admin", "admin")),
):
    try:
        created_employee = create_employee(employee)
        return {
            "employee_id": created_employee["employee_id"],
            "status": "created",
            "message": "Employee onboarding record created successfully.",
            "employee": created_employee,
        }
    except get_integrity_error_classes() as error:
        message = str(error)
        if is_duplicate_email_error(error):
            raise HTTPException(
                status_code=409,
                detail="An employee with this email already exists.",
            )
        raise HTTPException(status_code=400, detail=message)
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.get("")
def get_employees(
    limit: int = Query(default=25, ge=1, le=100),
    current_user=Depends(get_current_user),
):
    if is_hr_or_admin(current_user):
        employees = list_employees(limit=limit)
    elif current_user["role"] == "employee" and current_user.get("employee_id"):
        employee = get_employee_by_id(current_user["employee_id"])
        employees = [employee] if employee else []
    elif current_user["role"] == "manager":
        employees = []
        for user in list_users_by_manager_id(current_user["user_id"]):
            if user.get("employee_id"):
                employee = get_employee_by_id(user["employee_id"])
                if employee:
                    employees.append(employee)
        employees = employees[:limit]
    else:
        employees = []

    return {
        "employee_count": len(employees),
        "employees": employees,
    }


@router.get("/{employee_id}")
def get_employee(employee_id: str, current_user=Depends(get_current_user)):
    assert_employee_access(current_user, employee_id)
    employee = get_employee_by_id(employee_id)

    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found.")

    return employee


@router.put("/{employee_id}")
def update_employee_record(
    employee_id: str,
    employee: EmployeeUpdateRequest,
    current_user=Depends(require_roles("hr_admin", "admin")),
):
    try:
        updated_employee = update_employee(employee_id, employee)

        if updated_employee is None:
            raise HTTPException(status_code=404, detail="Employee not found.")

        create_audit_log(
            employee_id=updated_employee["employee_id"],
            event_type="employee_updated",
            event_message="Employee onboarding record was updated.",
        )

        return {
            "employee_id": updated_employee["employee_id"],
            "status": "updated",
            "message": "Employee onboarding record updated successfully.",
            "employee": updated_employee,
        }
    except get_integrity_error_classes() as error:
        message = str(error)
        if is_duplicate_email_error(error):
            raise HTTPException(
                status_code=409,
                detail="An employee with this email already exists.",
            )
        raise HTTPException(status_code=400, detail=message)


@router.get("/{employee_id}/tasks")
def get_employee_tasks(employee_id: str, current_user=Depends(get_current_user)):
    assert_employee_access(current_user, employee_id)
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
        "pending_approval_count": len(
            get_approvals(
                employee_id=employee["employee_id"],
                approval_status="Awaiting Approval",
            )
        ),
        "tasks": tasks,
    }


@router.get("/{employee_id}/timeline")
def get_employee_timeline(employee_id: str, current_user=Depends(get_current_user)):
    assert_employee_access(current_user, employee_id)
    employee = get_employee_by_id(employee_id)

    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found.")

    events = get_audit_logs(employee_id=employee_id, limit=100)

    return {
        "employee_id": employee["employee_id"],
        "event_count": len(events),
        "events": events,
    }


@router.post("/{employee_id}/generate-onboarding-plan")
def generate_onboarding_plan(employee_id: str, current_user=Depends(get_current_user)):
    if current_user["role"] not in {"manager", "hr_admin", "admin"}:
        raise HTTPException(status_code=403, detail="Insufficient permissions.")
    assert_employee_access(current_user, employee_id)
    final_state = run_onboarding_workflow_for_employee(employee_id)

    if final_state is None:
        raise HTTPException(status_code=404, detail="Employee not found.")

    tasks = final_state.get("onboarding_tasks", [])
    status_counts = Counter(task.get("task_status", "Unknown") for task in tasks)
    approval_required_count = sum(1 for task in tasks if task.get("approval_required"))
    employee_id = employee_id.upper()
    pending_approval_count = len(
        get_approvals(
            employee_id=employee_id,
            approval_status="Awaiting Approval",
        )
    )
    create_audit_log(
        employee_id=employee_id,
        event_type="workflow_plan_requested",
        event_message="Onboarding plan workflow was requested.",
        agent_name="supervisor",
        routing_reason=final_state.get("supervisor_routing_reason"),
    )

    return {
        "employee_id": employee_id,
        "workflow_run_id": final_state.get("workflow_run_id"),
        "workflow_status": final_state.get("workflow_status"),
        "next_agent": final_state.get("next_agent"),
        "routing_reason": final_state.get("supervisor_routing_reason"),
        "agent_outputs": final_state.get("agent_outputs"),
        "task_count": len(tasks),
        "status_counts": dict(status_counts),
        "approval_required_count": approval_required_count,
        "approval_count": pending_approval_count,
        "tasks": tasks,
    }
