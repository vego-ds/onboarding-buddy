from langgraph.graph import StateGraph, END

from agents.shared.workflow_state import WorkflowState
from agents.supervisor.routing import route_next_agent
from agents.intake.agent import run_intake_agent
from agents.task_planning.agent import run_task_planning_agent


def supervisor_node(state: WorkflowState) -> WorkflowState:
    return route_next_agent(state)


def intake_node(state: WorkflowState) -> WorkflowState:
    return run_intake_agent(state)


def task_planning_node(state: WorkflowState) -> WorkflowState:
    return run_task_planning_agent(state)


def route_from_supervisor(state: WorkflowState) -> str:
    next_agent = state.get("next_agent")

    if next_agent == "intake_agent":
        return "intake_agent"

    if next_agent == "task_planning_agent":
        return "task_planning_agent"

    if next_agent == "complete":
        return END

    if next_agent == "failure_handler":
        return END

    return END


def build_onboarding_graph():
    graph = StateGraph(WorkflowState)

    graph.add_node("supervisor", supervisor_node)
    graph.add_node("intake_agent", intake_node)
    graph.add_node("task_planning_agent", task_planning_node)

    graph.set_entry_point("supervisor")

    graph.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "intake_agent": "intake_agent",
            "task_planning_agent": "task_planning_agent",
            END: END,
        },
    )

    graph.add_edge("intake_agent", "supervisor")
    graph.add_edge("task_planning_agent", "supervisor")

    return graph.compile()
