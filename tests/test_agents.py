import pytest

from agents.shared.json_utils import parse_json_object
from agents.supervisor.routing import route_next_agent
from agents.task_planning.agent import normalize_llm_tasks, run_task_planning_agent


def valid_llm_tasks():
    return [
        {
            "task_name": "Send welcome email",
            "task_description": "Send the employee a welcome email.",
            "task_priority": "High",
            "approval_required": True,
            "assigned_owner": "HR",
        },
        {
            "task_name": "Collect employee documents",
            "task_description": "Collect identity and employment documents.",
            "task_priority": "High",
            "approval_required": True,
            "assigned_owner": "HR",
        },
        {
            "task_name": "Prepare laptop",
            "task_description": "Prepare laptop and core access.",
            "task_priority": "High",
            "approval_required": True,
            "assigned_owner": "IT",
        },
        {
            "task_name": "Schedule orientation",
            "task_description": "Schedule company orientation.",
            "task_priority": "Medium",
            "approval_required": False,
            "assigned_owner": "HR",
        },
        {
            "task_name": "Assign onboarding buddy",
            "task_description": "Assign a department buddy.",
            "task_priority": "Medium",
            "approval_required": False,
            "assigned_owner": "Manager",
        },
        {
            "task_name": "Complete profile setup",
            "task_description": "Complete employee profile setup.",
            "task_priority": "Low",
            "approval_required": False,
            "assigned_owner": "Employee",
        },
    ]


def test_parse_json_object_extracts_object_from_noisy_response():
    raw_response = '```json\n{"next_agent": "complete", "routing_reason": "done"}\n```'

    parsed = parse_json_object(raw_response)

    assert parsed["next_agent"] == "complete"
    assert parsed["routing_reason"] == "done"


def test_normalize_llm_tasks_requires_exact_task_count():
    with pytest.raises(ValueError, match="Expected 6"):
        normalize_llm_tasks(valid_llm_tasks()[:5])


def test_normalize_llm_tasks_rejects_duplicate_names():
    tasks = valid_llm_tasks()
    tasks[1]["task_name"] = tasks[0]["task_name"]

    with pytest.raises(ValueError, match="duplicate task"):
        normalize_llm_tasks(tasks)


def test_normalize_llm_tasks_rejects_invalid_owner():
    tasks = valid_llm_tasks()
    tasks[0]["assigned_owner"] = "Finance"

    with pytest.raises(ValueError, match="invalid owner"):
        normalize_llm_tasks(tasks)


def test_normalize_llm_tasks_returns_database_ready_tasks():
    tasks = normalize_llm_tasks(valid_llm_tasks())

    assert len(tasks) == 6
    assert tasks[0]["task_status"] == "Pending"
    assert tasks[0]["generated_by_agent"] == "task_planning_agent"


def test_task_planning_failure_records_agent_output():
    state = {
        "employee_id": "EMP_TEST",
        "employee_validated": False,
        "agent_outputs": {},
        "agent_execution_history": [],
    }

    result = run_task_planning_agent(state)

    assert result["workflow_status"] == "FAILED"
    assert result["agent_outputs"]["task_planning_agent"]["status"] == "failed"
    assert result["agent_execution_history"][-1]["status"] == "failed"


def test_supervisor_uses_deterministic_route_for_complete_state(monkeypatch):
    def fail_if_called(*args, **kwargs):
        raise AssertionError("LLM should not be called for complete deterministic route.")

    monkeypatch.setattr("agents.supervisor.routing.call_openrouter", fail_if_called)

    state = {
        "employee_validated": True,
        "onboarding_tasks": [{"task_name": "Send welcome email"}],
        "workflow_status": "RUNNING",
    }

    result = route_next_agent(state)

    assert result["next_agent"] == "complete"
    assert result["workflow_status"] == "COMPLETED"
