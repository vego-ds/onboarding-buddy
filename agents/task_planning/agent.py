from agents.shared.json_utils import parse_json_object
from agents.task_planning.prompts import (
    TASK_PLANNING_SYSTEM_PROMPT,
    build_task_planning_user_prompt,
)
from database.repositories.task_repository import (
    create_tasks,
    get_tasks_by_employee_id,
)
from llm.openrouter_client import call_openrouter

ALLOWED_PRIORITIES = {"Low", "Medium", "High"}
ALLOWED_OWNERS = {"HR", "IT", "Manager", "Employee"}
EXPECTED_TASK_COUNT = 6


def build_default_tasks(state):
    role = state.get("role", "Employee")
    department = state.get("department", "General")

    return [
        {
            "task_name": "Send welcome email",
            "task_description": f"Send a welcome email to the new {role} in the {department} department.",
            "task_status": "Pending",
            "task_priority": "High",
            "approval_required": True,
            "generated_by_agent": "task_planning_agent",
            "assigned_owner": "HR",
        },
        {
            "task_name": "Collect employee documents",
            "task_description": "Collect identity, tax, and employment documents from the employee.",
            "task_status": "Pending",
            "task_priority": "High",
            "approval_required": True,
            "generated_by_agent": "task_planning_agent",
            "assigned_owner": "HR",
        },
        {
            "task_name": "Prepare laptop and system access",
            "task_description": f"Prepare laptop, email, and required tools for the {role} role.",
            "task_status": "Pending",
            "task_priority": "High",
            "approval_required": True,
            "generated_by_agent": "task_planning_agent",
            "assigned_owner": "IT",
        },
        {
            "task_name": "Schedule orientation session",
            "task_description": "Schedule company orientation session for the new employee.",
            "task_status": "Pending",
            "task_priority": "Medium",
            "approval_required": False,
            "generated_by_agent": "task_planning_agent",
            "assigned_owner": "HR",
        },
        {
            "task_name": "Assign onboarding buddy",
            "task_description": f"Assign a buddy from the {department} department.",
            "task_status": "Pending",
            "task_priority": "Medium",
            "approval_required": False,
            "generated_by_agent": "task_planning_agent",
            "assigned_owner": "Manager",
        },
        {
            "task_name": "Review role-specific tools",
            "task_description": f"Review and prepare role-specific tools required for the {role} role.",
            "task_status": "Pending",
            "task_priority": "Medium",
            "approval_required": True,
            "generated_by_agent": "task_planning_agent",
            "assigned_owner": "Manager",
        },
    ]


def normalize_llm_tasks(tasks):
    if not isinstance(tasks, list):
        raise ValueError("Task Planning LLM returned tasks in an invalid format.")

    if len(tasks) != EXPECTED_TASK_COUNT:
        raise ValueError(
            f"Task Planning LLM returned {len(tasks)} tasks. Expected {EXPECTED_TASK_COUNT}."
        )

    normalized_tasks = []
    seen_task_names = set()

    for index, task in enumerate(tasks, start=1):
        if not isinstance(task, dict):
            raise ValueError(f"Task {index} is not a valid object.")

        task_name = str(task.get("task_name", "")).strip()
        task_description = str(task.get("task_description", "")).strip()
        task_priority = str(task.get("task_priority", "Medium")).strip().title()
        assigned_owner = str(task.get("assigned_owner", "HR")).strip()

        if not task_name:
            raise ValueError(f"Task {index} is missing task_name.")

        if task_name.lower() in seen_task_names:
            raise ValueError(f"Task Planning LLM returned duplicate task: {task_name}")

        if task_priority not in ALLOWED_PRIORITIES:
            raise ValueError(f"Task {index} has invalid priority: {task_priority}")

        if assigned_owner not in ALLOWED_OWNERS:
            raise ValueError(f"Task {index} has invalid owner: {assigned_owner}")

        approval_required = task.get("approval_required", False)
        if not isinstance(approval_required, bool):
            raise ValueError(f"Task {index} has invalid approval_required value.")

        seen_task_names.add(task_name.lower())
        normalized_tasks.append(
            {
                "task_name": task_name,
                "task_description": task_description,
                "task_status": "Pending",
                "task_priority": task_priority,
                "approval_required": approval_required,
                "generated_by_agent": "task_planning_agent",
                "assigned_owner": assigned_owner,
            }
        )

    return normalized_tasks


def generate_tasks_with_llm(state):
    user_prompt = build_task_planning_user_prompt(state)

    raw_response = call_openrouter(
        system_prompt=TASK_PLANNING_SYSTEM_PROMPT,
        user_prompt=user_prompt,
    )

    print("RAW TASK PLANNING LLM RESPONSE:")
    print(raw_response)

    if not raw_response:
        raise ValueError("Task Planning LLM returned empty response.")

    parsed_response = parse_json_object(raw_response)
    tasks = parsed_response.get("tasks", [])

    if not tasks:
        raise ValueError("Task Planning LLM returned no tasks.")

    return normalize_llm_tasks(tasks)


def run_task_planning_agent(state):
    if not state.get("employee_validated"):
        return {
            **state,
            "workflow_status": "FAILED",
            "failure_reason": "Cannot generate tasks before employee validation.",
            "current_agent": "task_planning_agent",
            "agent_outputs": {
                **state.get("agent_outputs", {}),
                "task_planning_agent": {
                    "status": "failed",
                    "message": "Cannot generate tasks before employee validation.",
                },
            },
            "agent_execution_history": state.get("agent_execution_history", [])
            + [
                {
                    "agent": "task_planning_agent",
                    "status": "failed",
                    "summary": "Task planning blocked because employee validation was missing.",
                }
            ],
        }

    existing_tasks = get_tasks_by_employee_id(state["employee_id"])

    if existing_tasks:
        return {
            **state,
            "onboarding_tasks": existing_tasks,
            "current_agent": "task_planning_agent",
            "workflow_status": "RUNNING",
            "agent_outputs": {
                **state.get("agent_outputs", {}),
                "task_planning_agent": {
                    "status": "skipped",
                    "task_count": len(existing_tasks),
                    "message": "Existing onboarding tasks found. Skipped duplicate task generation.",
                },
            },
            "agent_execution_history": state.get("agent_execution_history", [])
            + [
                {
                    "agent": "task_planning_agent",
                    "status": "skipped",
                    "summary": f"Found {len(existing_tasks)} existing tasks. Skipped generation.",
                }
            ],
        }

    try:
        generated_tasks = generate_tasks_with_llm(state)
        generation_source = "llm"

    except Exception as error:
        print(f"Task Planning LLM failed. Using fallback tasks. Error: {error}")
        generated_tasks = build_default_tasks(state)
        generation_source = "fallback"

    saved_tasks = create_tasks(state["employee_id"], generated_tasks)

    return {
        **state,
        "onboarding_tasks": saved_tasks,
        "current_agent": "task_planning_agent",
        "workflow_status": "RUNNING",
        "agent_outputs": {
            **state.get("agent_outputs", {}),
            "task_planning_agent": {
                "status": "success",
                "task_count": len(saved_tasks),
                "generation_source": generation_source,
                "message": "Onboarding tasks generated and saved successfully.",
            },
        },
        "agent_execution_history": state.get("agent_execution_history", [])
        + [
            {
                "agent": "task_planning_agent",
                "status": "success",
                "summary": f"Generated {len(saved_tasks)} onboarding tasks using {generation_source}.",
            }
        ],
    }
