CREATE TABLE IF NOT EXISTS tenants (
    tenant_id TEXT PRIMARY KEY,
    tenant_name TEXT NOT NULL,
    tenant_domain TEXT UNIQUE,
    sso_provider TEXT,
    sso_issuer TEXT,
    sso_audience TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS employees (
    employee_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL DEFAULT 'TENANT_DEFAULT',
    employee_name TEXT NOT NULL,
    employee_email TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL,
    department TEXT NOT NULL,
    joining_date TEXT NOT NULL,
    onboarding_status TEXT DEFAULT 'PENDING',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
);

CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL DEFAULT 'TENANT_DEFAULT',
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    employee_id TEXT,
    manager_id TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
    FOREIGN KEY (manager_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS refresh_tokens (
    refresh_token_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    token_hash TEXT NOT NULL UNIQUE,
    expires_at TEXT NOT NULL,
    revoked_at TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS password_reset_tokens (
    reset_token_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    token_hash TEXT NOT NULL UNIQUE,
    expires_at TEXT NOT NULL,
    used_at TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS auth_audit_logs (
    auth_audit_id TEXT PRIMARY KEY,
    tenant_id TEXT,
    user_id TEXT,
    email TEXT,
    event_type TEXT NOT NULL,
    event_status TEXT NOT NULL,
    event_message TEXT NOT NULL,
    ip_address TEXT,
    user_agent TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS onboarding_tasks (
    task_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL DEFAULT 'TENANT_DEFAULT',
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
    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

CREATE TABLE IF NOT EXISTS task_dependencies (
    dependency_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL DEFAULT 'TENANT_DEFAULT',
    employee_id TEXT NOT NULL,
    task_id TEXT NOT NULL,
    depends_on_task_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
    FOREIGN KEY (task_id) REFERENCES onboarding_tasks(task_id),
    FOREIGN KEY (depends_on_task_id) REFERENCES onboarding_tasks(task_id),
    UNIQUE (task_id, depends_on_task_id)
);

CREATE TABLE IF NOT EXISTS approvals (
    approval_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL DEFAULT 'TENANT_DEFAULT',
    employee_id TEXT NOT NULL,
    related_task_id TEXT,
    action_type TEXT NOT NULL,
    approval_status TEXT DEFAULT 'Awaiting Approval',
    review_notes TEXT,
    reviewed_by TEXT,
    reviewed_at TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

CREATE TABLE IF NOT EXISTS audit_logs (
    log_id TEXT PRIMARY KEY,
    tenant_id TEXT DEFAULT 'TENANT_DEFAULT',
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
    tenant_id TEXT NOT NULL DEFAULT 'TENANT_DEFAULT',
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
    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

CREATE TABLE IF NOT EXISTS agent_runs (
    agent_run_id TEXT PRIMARY KEY,
    tenant_id TEXT DEFAULT 'TENANT_DEFAULT',
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
    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id),
    FOREIGN KEY (workflow_run_id) REFERENCES workflow_runs(workflow_run_id),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

CREATE TABLE IF NOT EXISTS workflow_state (
    state_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL DEFAULT 'TENANT_DEFAULT',
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
    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id),
    FOREIGN KEY (workflow_run_id) REFERENCES workflow_runs(workflow_run_id),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

CREATE TABLE IF NOT EXISTS knowledge_chunks (
    chunk_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL DEFAULT 'TENANT_DEFAULT',
    source TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    embedding_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id),
    UNIQUE (tenant_id, source, content_hash)
);

INSERT INTO tenants (
    tenant_id,
    tenant_name,
    tenant_domain,
    created_at,
    updated_at
)
VALUES (
    'TENANT_DEFAULT',
    'Default Tenant',
    NULL,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
)
ON CONFLICT (tenant_id) DO NOTHING;

CREATE INDEX IF NOT EXISTS idx_employees_created_at
ON employees(created_at);

CREATE INDEX IF NOT EXISTS idx_employees_tenant_id
ON employees(tenant_id);

CREATE INDEX IF NOT EXISTS idx_users_email
ON users(email);

CREATE INDEX IF NOT EXISTS idx_users_tenant_id
ON users(tenant_id);

CREATE INDEX IF NOT EXISTS idx_users_role
ON users(role);

CREATE INDEX IF NOT EXISTS idx_users_employee_id
ON users(employee_id);

CREATE INDEX IF NOT EXISTS idx_users_manager_id
ON users(manager_id);

CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id
ON refresh_tokens(user_id);

CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token_hash
ON refresh_tokens(token_hash);

CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_user_id
ON password_reset_tokens(user_id);

CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_token_hash
ON password_reset_tokens(token_hash);

CREATE INDEX IF NOT EXISTS idx_auth_audit_logs_user_created_at
ON auth_audit_logs(user_id, created_at);

CREATE INDEX IF NOT EXISTS idx_auth_audit_logs_tenant_created_at
ON auth_audit_logs(tenant_id, created_at);

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
