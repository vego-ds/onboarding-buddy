import pytest
from fastapi import HTTPException

from backend.routes import workflows


def test_workflow_run_detail_normalizes_id_and_includes_agent_runs(monkeypatch):
    calls = {}

    def fake_get_workflow_run_by_id(workflow_run_id):
        calls["workflow_run_id"] = workflow_run_id
        return {
            "workflow_run_id": workflow_run_id,
            "employee_id": "EMP_1",
            "workflow_status": "COMPLETED",
            "started_at": "2026-06-03T00:00:00+00:00",
            "completed_at": "2026-06-03T00:01:00+00:00",
        }

    def fake_get_agent_runs(workflow_run_id=None, employee_id=None):
        calls["agent_workflow_run_id"] = workflow_run_id
        return [
            {
                "agent_run_id": "AGENT_RUN_1",
                "workflow_run_id": workflow_run_id,
                "employee_id": "EMP_1",
                "agent_name": "intake_agent",
                "agent_role": "intake_agent",
                "execution_order": 1,
                "execution_status": "Success",
                "started_at": "2026-06-03T00:00:00+00:00",
                "completed_at": "2026-06-03T00:01:00+00:00",
            }
        ]

    monkeypatch.setattr(workflows, "get_workflow_run_by_id", fake_get_workflow_run_by_id)
    monkeypatch.setattr(workflows, "get_agent_runs", fake_get_agent_runs)

    response = workflows.get_workflow_run(" wf_f32245a0 ")

    assert calls["workflow_run_id"] == "WF_F32245A0"
    assert calls["agent_workflow_run_id"] == "WF_F32245A0"
    assert response["workflow_run_id"] == "WF_F32245A0"
    assert response["employee_id"] == "EMP_1"
    assert response["workflow_status"] == "COMPLETED"
    assert response["started_at"] == "2026-06-03T00:00:00+00:00"
    assert response["completed_at"] == "2026-06-03T00:01:00+00:00"
    assert response["agent_run_count"] == 1
    assert response["agent_runs"][0]["agent_name"] == "intake_agent"


def test_workflow_run_detail_returns_404_for_missing_run(monkeypatch):
    monkeypatch.setattr(workflows, "get_workflow_run_by_id", lambda workflow_run_id: None)

    with pytest.raises(HTTPException) as error:
        workflows.get_workflow_run("WF_MISSING")

    assert error.value.status_code == 404
    assert error.value.detail == "Workflow run not found."
