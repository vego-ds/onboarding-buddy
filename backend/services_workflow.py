from agents.workflow.graph import build_onboarding_graph
from database.repositories.employee_repository import (
    get_employee_by_id,
    update_employee_status,
)


def run_onboarding_workflow_for_employee(employee_id: str):
    employee = get_employee_by_id(employee_id)

    if employee is None:
        return None

    initial_state = {
        "employee_id": employee["employee_id"],
        "employee_name": employee["employee_name"],
        "employee_email": employee["employee_email"],
        "role": employee["role"],
        "department": employee["department"],
        "joining_date": employee["joining_date"],
        "employee_validated": False,
        "onboarding_tasks": [],
        "workflow_status": "STARTED",
        "agent_outputs": {},
        "agent_execution_history": [],
    }

    app = build_onboarding_graph()

    final_state = app.invoke(
        initial_state,
        config={"recursion_limit": 10},
    )

    if final_state.get("workflow_status") == "FAILED":
        update_employee_status(employee_id, "FAILED")
    elif final_state.get("onboarding_tasks"):
        update_employee_status(employee_id, "PLAN_READY")

    return final_state
