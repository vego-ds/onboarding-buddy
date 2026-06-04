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

CREATE TABLE IF NOT EXISTS task_dependencies (
    dependency_id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    task_id TEXT NOT NULL,
    depends_on_task_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
    FOREIGN KEY (task_id) REFERENCES onboarding_tasks(task_id),
    FOREIGN KEY (depends_on_task_id) REFERENCES onboarding_tasks(task_id),
    UNIQUE (task_id, depends_on_task_id)
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
    completed_at TEXT,
    FOREIGN KEY (workflow_run_id) REFERENCES workflow_runs(workflow_run_id),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
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
    updated_at TEXT NOT NULL,
    FOREIGN KEY (workflow_run_id) REFERENCES workflow_runs(workflow_run_id),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

CREATE TABLE IF NOT EXISTS knowledge_chunks (
    chunk_id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    embedding_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE (source, content_hash)
);

CREATE INDEX IF NOT EXISTS idx_employees_created_at
ON employees(created_at);

CREATE INDEX IF NOT EXISTS idx_employees_onboarding_status
ON employees(onboarding_status);

CREATE INDEX IF NOT EXISTS idx_onboarding_tasks_employee_id
ON onboarding_tasks(employee_id);

CREATE INDEX IF NOT EXISTS idx_onboarding_tasks_status
ON onboarding_tasks(task_status);

CREATE INDEX IF NOT EXISTS idx_task_dependencies_task_id
ON task_dependencies(task_id);

CREATE INDEX IF NOT EXISTS idx_approvals_employee_id
ON approvals(employee_id);

CREATE INDEX IF NOT EXISTS idx_approvals_related_task_id
ON approvals(related_task_id);

CREATE INDEX IF NOT EXISTS idx_approvals_status
ON approvals(approval_status);

CREATE INDEX IF NOT EXISTS idx_audit_logs_employee_id_timestamp
ON audit_logs(employee_id, timestamp);

CREATE INDEX IF NOT EXISTS idx_audit_logs_workflow_run_id
ON audit_logs(workflow_run_id);

CREATE INDEX IF NOT EXISTS idx_workflow_runs_employee_id_started_at
ON workflow_runs(employee_id, started_at);

CREATE INDEX IF NOT EXISTS idx_workflow_runs_status
ON workflow_runs(workflow_status);

CREATE INDEX IF NOT EXISTS idx_agent_runs_workflow_run_id
ON agent_runs(workflow_run_id);

CREATE INDEX IF NOT EXISTS idx_agent_runs_employee_id
ON agent_runs(employee_id);

CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_source
ON knowledge_chunks(source);

CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_content_hash
ON knowledge_chunks(content_hash);
