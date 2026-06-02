from typing import TypedDict, List, Dict, Optional, Any


class WorkflowState(TypedDict, total=False):
    workflow_run_id: str
    employee_id: str
    employee_name: str
    employee_email: str
    role: str
    department: str
    joining_date: str

    employee_validated: bool
    missing_fields: List[str]

    onboarding_tasks: List[Dict[str, Any]]
    approval_records: List[Dict[str, Any]]
    task_dependencies: List[Dict[str, Any]]

    current_agent: str
    next_agent: str
    supervisor_routing_reason: str

    workflow_status: str
    failure_reason: Optional[str]

    agent_outputs: Dict[str, Any]
    agent_execution_history: List[Dict[str, Any]]
