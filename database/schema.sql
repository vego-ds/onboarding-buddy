CREATE TABLE IF NOT EXISTS employees (
    employee_id TEXT PRIMARY KEY,
    employee_name TEXT NOT NULL,
    employee_email TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL,
    department TEXT NOT NULL,
    joining_date TEXT NOT NULL,
    onboarding_status TEXT DEFAULT 'PENDING',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS onboarding_tasks (
    task_id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    task_name TEXT NOT NULL,
    task_description TEXT,
    task_status TEXT DEFAULT 'Pending',
    task_priority TEXT DEFAULT 'Medium',
    approval_required INTEGER DEFAULT 0,
    generated_by_agent TEXT,
    assigned_owner TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

CREATE TABLE IF NOT EXISTS approvals (
    approval_id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    related_task_id TEXT,
    action_type TEXT NOT NULL,
    approval_status TEXT DEFAULT 'Awaiting Approval',
    review_notes TEXT,
    reviewed_by TEXT,
    reviewed_at TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

CREATE TABLE IF NOT EXISTS audit_logs (
    log_id TEXT PRIMARY KEY,
    employee_id TEXT,
    workflow_run_id TEXT,
    event_type TEXT NOT NULL,
    event_message TEXT NOT NULL,
    agent_name TEXT,
    routing_reason TEXT,
    event_status TEXT DEFAULT 'Success',
    timestamp TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS workflow_runs (
    workflow_run_id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    workflow_status TEXT DEFAULT 'Running',
    current_node TEXT,
    current_agent TEXT,
    next_agent TEXT,
    retry_count INTEGER DEFAULT 0,
    failure_reason TEXT,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    llm_provider TEXT DEFAULT 'OpenRouter',
    llm_model TEXT,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

CREATE TABLE IF NOT EXISTS agent_runs (
    agent_run_id TEXT PRIMARY KEY,
    workflow_run_id TEXT,
    employee_id TEXT,
    agent_name TEXT NOT NULL,
    agent_role TEXT NOT NULL,
    execution_order INTEGER,
    input_summary TEXT,
    output_summary TEXT,
    routing_reason TEXT,
    execution_status TEXT DEFAULT 'Success',
    retry_count INTEGER DEFAULT 0,
    execution_duration_ms INTEGER,
    llm_provider TEXT DEFAULT 'OpenRouter',
    llm_model TEXT,
    started_at TEXT NOT NULL,
    completed_at TEXT
);

CREATE TABLE IF NOT EXISTS workflow_state (
    state_id TEXT PRIMARY KEY,
    workflow_run_id TEXT NOT NULL,
    employee_id TEXT NOT NULL,
    current_node TEXT,
    current_agent TEXT,
    next_agent TEXT,
    workflow_status TEXT DEFAULT 'Running',
    onboarding_tasks_json TEXT,
    approval_status TEXT,
    retry_count INTEGER DEFAULT 0,
    failure_reason TEXT,
    workflow_context_json TEXT,
    agent_execution_history_json TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);