from fastapi import APIRouter, HTTPException, Query

from database.repositories.workflow_run_repository import (
    get_agent_runs,
    get_workflow_run_by_id,
    get_workflow_runs,
    normalize_workflow_run_id,
)

router = APIRouter(prefix="/workflow-runs", tags=["Workflow Runs"])


@router.get("")
def list_workflow_runs(
    employee_id: str | None = None,
    limit: int = Query(default=25, ge=1, le=100),
):
    workflow_runs = get_workflow_runs(employee_id=employee_id, limit=limit)

    return {
        "workflow_run_count": len(workflow_runs),
        "workflow_runs": workflow_runs,
    }


@router.get("/{workflow_run_id}")
def get_workflow_run(workflow_run_id: str):
    workflow_run_id = normalize_workflow_run_id(workflow_run_id)
    workflow_run = get_workflow_run_by_id(workflow_run_id)

    if workflow_run is None:
        raise HTTPException(status_code=404, detail="Workflow run not found.")

    agent_runs = get_agent_runs(workflow_run_id=workflow_run_id)

    return {
        "workflow_run_id": workflow_run["workflow_run_id"],
        "employee_id": workflow_run["employee_id"],
        "workflow_status": workflow_run["workflow_status"],
        "started_at": workflow_run["started_at"],
        "completed_at": workflow_run.get("completed_at"),
        "workflow_run": workflow_run,
        "agent_run_count": len(agent_runs),
        "agent_runs": agent_runs,
    }
