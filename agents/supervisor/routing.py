import json

from agents.supervisor.prompts import (
    SUPERVISOR_SYSTEM_PROMPT,
    build_supervisor_user_prompt,
)
from llm.openrouter_client import call_openrouter


ALLOWED_ROUTES = {
    "intake_agent",
    "task_planning_agent",
    "complete",
    "failure_handler",
}


def deterministic_route(state):
    if state.get("failure_reason"):
        return "failure_handler", state["failure_reason"]

    if not state.get("employee_validated"):
        return "intake_agent", "Employee profile has not been validated yet."

    if not state.get("onboarding_tasks"):
        return "task_planning_agent", "Employee is validated. Onboarding tasks need to be generated."

    return "complete", "Employee is validated and onboarding tasks exist. Workflow can complete."


def route_next_agent(state):
    deterministic_next_agent, deterministic_reason = deterministic_route(state)

    if deterministic_next_agent == "complete":
        return {
            **state,
            "next_agent": "complete",
            "current_agent": "supervisor",
            "workflow_status": "COMPLETED",
            "supervisor_routing_reason": deterministic_reason,
        }

    try:
        user_prompt = build_supervisor_user_prompt(state)

        raw_response = call_openrouter(
            system_prompt=SUPERVISOR_SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        print("RAW SUPERVISOR LLM RESPONSE:")
        print(raw_response)

        if not raw_response:
            raise ValueError("Supervisor LLM returned empty response.")

        decision = json.loads(raw_response)

        next_agent = decision.get("next_agent")
        routing_reason = decision.get("routing_reason")

        if next_agent not in ALLOWED_ROUTES:
            raise ValueError(f"Invalid supervisor route: {next_agent}")

        if next_agent != deterministic_next_agent:
            next_agent = deterministic_next_agent
            routing_reason = deterministic_reason

        return {
            **state,
            "next_agent": next_agent,
            "current_agent": "supervisor",
            "workflow_status": state.get("workflow_status", "RUNNING"),
            "supervisor_routing_reason": routing_reason,
        }

    except Exception as error:
        print(f"LLM supervisor failed. Using deterministic route. Error: {error}")

        return {
            **state,
            "next_agent": deterministic_next_agent,
            "current_agent": "supervisor",
            "workflow_status": "COMPLETED"
            if deterministic_next_agent == "complete"
            else state.get("workflow_status", "RUNNING"),
            "supervisor_routing_reason": deterministic_reason,
        }
