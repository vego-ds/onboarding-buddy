import json

from agents.task_planning.prompts import (
    TASK_PLANNING_SYSTEM_PROMPT,
    build_task_planning_user_prompt,
)
from database.repositories.task_repository import (
    create_tasks,
    get_tasks_by_employee_id,
)
from llm.openrouter_client import call_openrouter


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
    normalized_tasks = []

    for task in tasks:
        normalized_tasks.append(
            {
                "task_name": task.get("task_name", "Untitled onboarding task"),
                "task_description": task.get("task_description", ""),
                "task_status": "Pending",
                "task_priority": task.get("task_priority", "Medium"),
                "approval_required": bool(task.get("approval_required", False)),
                "generated_by_agent": "task_planning_agent",
                "assigned_owner": task.get("assigned_owner", "HR"),
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

    parsed_response = json.loads(raw_response)
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
