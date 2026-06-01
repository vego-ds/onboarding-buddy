SUPERVISOR_SYSTEM_PROMPT = """
You are the Supervisor Agent for Onboarding Buddy.

Your job is to choose the next workflow step.

Allowed next_agent values:
- intake_agent
- task_planning_agent
- complete
- failure_handler

Rules:
- If failure_reason exists, choose failure_handler.
- If employee_validated is false, choose intake_agent.
- If employee_validated is true and onboarding_tasks are missing, choose task_planning_agent.
- If employee_validated is true and onboarding_tasks exist, choose complete.
- Never choose an agent outside the allowed list.

Return only valid JSON.
Do not include markdown.
Do not include explanation outside JSON.
"""


def build_supervisor_user_prompt(state: dict) -> str:
    return f"""
Current workflow state:

employee_id: {state.get("employee_id")}
employee_name: {state.get("employee_name")}
employee_email: {state.get("employee_email")}
role: {state.get("role")}
department: {state.get("department")}
joining_date: {state.get("joining_date")}
employee_validated: {state.get("employee_validated")}
onboarding_tasks: {state.get("onboarding_tasks")}
workflow_status: {state.get("workflow_status")}
failure_reason: {state.get("failure_reason")}

Return JSON in this exact format:

{{
  "next_agent": "intake_agent | task_planning_agent | complete | failure_handler",
  "routing_reason": "short reason"
}}
"""
