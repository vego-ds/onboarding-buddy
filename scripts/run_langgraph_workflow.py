import sys

from agents.workflow.graph import build_onboarding_graph
from database.repositories.employee_repository import get_employee_by_id


def run_langgraph_workflow(employee_id: str):
    employee = get_employee_by_id(employee_id)

    if employee is None:
        print(f"Employee not found: {employee_id}")
        return

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

    print("\nLANGGRAPH WORKFLOW COMPLETE")
    print(final_state)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.run_langgraph_workflow EMPLOYEE_ID")
    else:
        run_langgraph_workflow(sys.argv[1])
