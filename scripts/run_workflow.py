import sys

from agents.supervisor.routing import route_next_agent
from agents.intake.agent import run_intake_agent
from database.repositories.employee_repository import get_employee_by_id


def run_basic_workflow(employee_id: str):
    employee = get_employee_by_id(employee_id)

    if employee is None:
        print(f"Employee not found: {employee_id}")
        return

    state = {
        "employee_id": employee["employee_id"],
        "employee_name": employee["employee_name"],
        "employee_email": employee["employee_email"],
        "role": employee["role"],
        "department": employee["department"],
        "joining_date": employee["joining_date"],
        "employee_validated": False,
        "workflow_status": "STARTED",
        "agent_outputs": {},
        "agent_execution_history": [],
    }

    print("\nSTARTING WORKFLOW")
    print(state)

    state = route_next_agent(state)
    print("\nSUPERVISOR ROUTED TO:")
    print(state["next_agent"])
    print(state["supervisor_routing_reason"])

    if state["next_agent"] == "intake_agent":
        state = run_intake_agent(state)
        print("\nINTAKE AGENT RESULT:")
        print(state["agent_outputs"]["intake_agent"])

    state = route_next_agent(state)
    print("\nFINAL SUPERVISOR DECISION:")
    print(state["next_agent"])
    print(state["supervisor_routing_reason"])

    print("\nFINAL WORKFLOW STATE:")
    print(state)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.run_workflow EMPLOYEE_ID")
    else:
        run_basic_workflow(sys.argv[1])
