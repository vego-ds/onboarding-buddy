REQUIRED_FIELDS = [
    "employee_id",
    "employee_name",
    "employee_email",
    "role",
    "department",
    "joining_date",
]


def run_intake_agent(state):
    missing_fields = []

    for field in REQUIRED_FIELDS:
        if not state.get(field):
            missing_fields.append(field)

    if missing_fields:
        return {
            **state,
            "employee_validated": False,
            "missing_fields": missing_fields,
            "current_agent": "intake_agent",
            "workflow_status": "FAILED",
            "failure_reason": f"Missing required fields: {', '.join(missing_fields)}",
            "agent_outputs": {
                **state.get("agent_outputs", {}),
                "intake_agent": {
                    "status": "failed",
                    "missing_fields": missing_fields,
                },
            },
            "agent_execution_history": state.get("agent_execution_history", [])
            + [
                {
                    "agent": "intake_agent",
                    "status": "failed",
                    "summary": "Employee validation failed.",
                }
            ],
        }

    return {
        **state,
        "employee_validated": True,
        "missing_fields": [],
        "current_agent": "intake_agent",
        "workflow_status": "RUNNING",
        "failure_reason": None,
        "agent_outputs": {
            **state.get("agent_outputs", {}),
            "intake_agent": {
                "status": "success",
                "message": "Employee profile validated successfully.",
            },
        },
        "agent_execution_history": state.get("agent_execution_history", [])
        + [
            {
                "agent": "intake_agent",
                "status": "success",
                "summary": "Employee profile validated successfully.",
            }
        ],
    }
