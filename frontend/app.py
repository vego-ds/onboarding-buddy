from collections import Counter
from datetime import date
from html import escape

import requests
import streamlit as st

REQUEST_TIMEOUT = 30


def get_api_base_url():
    try:
        return st.secrets.get("API_BASE_URL", "http://127.0.0.1:8000")
    except Exception:
        return "http://127.0.0.1:8000"


API_BASE_URL = get_api_base_url()

st.set_page_config(
    page_title="Onboarding Buddy",
    page_icon="OB",
    layout="wide",
)


def inject_styles():
    st.markdown(
        """
        <style>
        :root {
            --bg: #f4f6f8;
            --surface: #ffffff;
            --surface-subtle: #f8fafc;
            --ink: #111827;
            --heading: #0f172a;
            --muted: #64748b;
            --line: #d8e0ea;
            --line-strong: #c4cfdd;
            --accent: #2563eb;
            --accent-soft: #eff6ff;
            --success: #15803d;
            --success-soft: #ecfdf3;
            --warning: #b45309;
            --warning-soft: #fff7ed;
            --danger: #b91c1c;
            --danger-soft: #fef2f2;
            --shadow: 0 12px 28px rgba(15, 23, 42, 0.07);
            --radius: 10px;
        }
        .stApp {
            background: var(--bg);
            color: var(--ink);
        }
        .block-container {
            max-width: 1280px;
            padding-top: 1rem;
            padding-bottom: 2rem;
        }
        [data-testid="stHeader"] {
            background: transparent;
        }
        section[data-testid="stSidebar"] {
            background: #0f172a;
        }
        section[data-testid="stSidebar"] * {
            color: #e5e7eb;
        }
        section[data-testid="stSidebar"] .stButton > button {
            background: rgba(255, 255, 255, 0.08);
            border-color: rgba(255, 255, 255, 0.18);
            color: #ffffff !important;
        }
        .app-header {
            background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
            border-radius: 14px;
            box-shadow: var(--shadow);
            color: #ffffff;
            padding: 1.35rem 1.5rem;
            margin-bottom: 1.1rem;
        }
        .app-title {
            font-size: 2rem;
            line-height: 1.1;
            font-weight: 760;
            letter-spacing: 0;
            margin: 0;
            color: #ffffff;
        }
        .app-subtitle {
            color: #cbd5e1;
            font-size: 1rem;
            margin: 0.35rem 0 0;
            max-width: 820px;
        }
        .section-kicker {
            color: var(--muted);
            font-size: 0.78rem;
            font-weight: 750;
            letter-spacing: 0.04em;
            margin-bottom: 0.25rem;
            text-transform: uppercase;
        }
        .section-title {
            color: var(--heading);
            font-size: 1.35rem;
            font-weight: 760;
            line-height: 1.2;
            margin: 0 0 0.8rem;
        }
        .metric-strip {
            display: grid;
            grid-template-columns: repeat(6, minmax(0, 1fr));
            gap: 0.75rem;
            margin: 0.35rem 0 1.1rem;
        }
        .metric-tile,
        .employee-panel,
        .task-card,
        .profile-card,
        .workflow-card,
        .empty-state {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: var(--radius);
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
        }
        .metric-tile {
            border-left: 4px solid transparent;
            padding: 0.85rem 0.95rem;
            min-height: 92px;
        }
        .metric-tile-active {
            border-color: var(--accent);
            box-shadow: var(--shadow);
        }
        .metric-label {
            color: var(--muted);
            font-size: 0.78rem;
            font-weight: 750;
            text-transform: uppercase;
            margin-bottom: 0.4rem;
        }
        .metric-value {
            color: var(--heading);
            font-size: 1.55rem;
            font-weight: 760;
            line-height: 1.1;
        }
        .metric-help {
            color: var(--muted);
            font-size: 0.78rem;
            margin-top: 0.3rem;
        }
        .employee-panel,
        .task-card,
        .profile-card,
        .workflow-card {
            padding: 1rem;
            margin-bottom: 0.75rem;
        }
        .employee-name,
        .task-title {
            color: var(--heading);
            font-size: 1rem;
            font-weight: 740;
            line-height: 1.35;
        }
        .employee-meta,
        .task-description {
            color: var(--muted);
            font-size: 0.9rem;
            line-height: 1.45;
        }
        .task-title-row {
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 0.35rem;
        }
        .employee-row {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 1rem;
        }
        .chip-row {
            display: flex;
            gap: 0.45rem;
            flex-wrap: wrap;
            margin-top: 0.65rem;
        }
        .chip {
            border-radius: 999px;
            border: 1px solid var(--line);
            color: var(--heading);
            background: var(--surface-subtle);
            font-size: 0.74rem;
            font-weight: 650;
            padding: 0.16rem 0.55rem;
            white-space: nowrap;
        }
        .chip-high { background: var(--danger-soft); color: var(--danger); border-color: #fecaca; }
        .chip-medium { background: var(--warning-soft); color: var(--warning); border-color: #fed7aa; }
        .chip-low { background: var(--accent-soft); color: var(--accent); border-color: #bfdbfe; }
        .chip-status { background: var(--accent-soft); color: var(--accent); border-color: #bfdbfe; }
        .chip-success { background: var(--success-soft); color: var(--success); border-color: #bbf7d0; }
        .chip-warning { background: var(--warning-soft); color: var(--warning); border-color: #fed7aa; }
        .chip-danger { background: var(--danger-soft); color: var(--danger); border-color: #fecaca; }
        .chip-locked { background: var(--danger-soft); color: var(--danger); border-color: #fecaca; }
        .chip-unlocked { background: var(--success-soft); color: var(--success); border-color: #bbf7d0; }
        .task-card-locked {
            border-color: #fecaca;
            border-left: 4px solid var(--danger);
        }
        .task-card-ready {
            border-left: 4px solid var(--success);
        }
        .dependency-state {
            background: var(--surface-subtle);
            border: 1px solid var(--line);
            border-left: 4px solid var(--line-strong);
            border-radius: 8px;
            color: var(--muted);
            font-size: 0.86rem;
            line-height: 1.45;
            margin: 0.55rem 0 0.8rem;
            padding: 0.65rem 0.75rem;
        }
        .dependency-locked { border-left-color: var(--danger); }
        .dependency-ready { border-left-color: var(--success); }
        .timeline-item {
            border-left: 4px solid var(--accent);
        }
        .agent-step {
            border-left: 4px solid var(--accent);
            position: relative;
        }
        .empty-state {
            color: var(--muted);
            padding: 1.15rem;
            margin-top: 0.5rem;
            text-align: center;
        }
        .empty-title {
            color: var(--heading);
            font-weight: 760;
            margin-bottom: 0.25rem;
        }
        .error-box {
            background: var(--danger-soft);
            border: 1px solid #fecaca;
            border-radius: var(--radius);
            color: var(--danger);
            padding: 0.9rem 1rem;
            margin: 0.5rem 0;
        }
        .status-pill {
            align-items: center;
            border-radius: 999px;
            display: inline-flex;
            font-size: 0.78rem;
            font-weight: 760;
            gap: 0.35rem;
            padding: 0.22rem 0.65rem;
        }
        .status-online {
            background: var(--success-soft);
            color: var(--success);
        }
        .status-offline {
            background: var(--danger-soft);
            color: var(--danger);
        }
        .status-dot {
            border-radius: 999px;
            display: inline-block;
            height: 0.45rem;
            width: 0.45rem;
        }
        div[data-testid="stTabs"] button {
            color: var(--ink);
            font-weight: 650;
        }
        div[data-testid="stTabs"] button[aria-selected="true"] {
            color: var(--accent);
        }
        label,
        label p,
        .stMarkdown,
        .stSelectbox label,
        .stTextInput label,
        .stDateInput label {
            color: var(--ink);
        }
        .stTextInput input,
        .stDateInput input,
        div[data-baseweb="select"] > div {
            background: #ffffff;
            border-color: var(--line);
            color: var(--ink);
            border-radius: 8px;
        }
        .stButton > button,
        .stFormSubmitButton > button {
            background: #ffffff;
            border-radius: 8px;
            min-height: 2.65rem;
            font-weight: 700;
            border-color: var(--line);
            color: var(--ink) !important;
        }
        .stButton > button[kind="primary"],
        .stFormSubmitButton > button[kind="primary"] {
            background: var(--accent);
            border-color: var(--accent);
            color: #ffffff !important;
        }
        .stButton > button:hover,
        .stFormSubmitButton > button:hover {
            border-color: var(--accent);
        }
        @media (max-width: 900px) {
            .metric-strip {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
            .app-title {
                font-size: 1.8rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def request_api(method, path, **kwargs):
    timeout = kwargs.pop("timeout", REQUEST_TIMEOUT)
    try:
        response = requests.request(
            method,
            f"{API_BASE_URL}{path}",
            timeout=timeout,
            **kwargs,
        )
    except requests.RequestException as error:
        return None, f"Backend request failed: {error}"

    if response.ok:
        return response.json(), None

    try:
        detail = response.json().get("detail", response.text)
    except ValueError:
        detail = response.text

    return None, f"{response.status_code}: {detail}"


@st.cache_data(ttl=10)
def fetch_employees():
    data, error = request_api("GET", "/employees?limit=50")
    if error:
        return [], error
    return data.get("employees", []), None


@st.cache_data(ttl=10)
def fetch_approvals(approval_status=None):
    path = "/approvals"
    if approval_status:
        path = f"{path}?approval_status={approval_status}"

    data, error = request_api("GET", path)
    if error:
        return [], error
    return data.get("approvals", []), None


@st.cache_data(ttl=10)
def fetch_workflow_runs():
    data, error = request_api("GET", "/workflow-runs?limit=10")
    if error:
        return [], error
    return data.get("workflow_runs", []), None


def fetch_workflow_run(workflow_run_id):
    return request_api("GET", f"/workflow-runs/{workflow_run_id}")


def fetch_tasks(employee_id):
    return request_api("GET", f"/employees/{employee_id}/tasks")


def fetch_task_dependencies(task_id):
    return request_api("GET", f"/tasks/{task_id}/dependencies")


def fetch_employee_timeline(employee_id):
    return request_api("GET", f"/employees/{employee_id}/timeline")


def parse_joining_date(joining_date):
    try:
        return date.fromisoformat(joining_date)
    except (TypeError, ValueError):
        return date.today()


def normalize_employee_id(employee_id):
    return employee_id.strip().upper()


def format_status(status):
    return str(status or "Unknown").replace("_", " ").title()


def chip_class_for_status(status):
    normalized = format_status(status)
    if normalized in {"Completed", "Plan Ready", "Approved", "Success"}:
        return "chip-success"
    if normalized in {"Pending", "Awaiting Approval", "Running", "In Progress"}:
        return "chip-warning"
    if normalized in {"Blocked", "Failed", "Rejected"}:
        return "chip-danger"
    return "chip-status"


def employee_option_label(employee):
    return (
        f"{employee.get('employee_name', 'Unknown')} · "
        f"{employee.get('role', 'Role')} · "
        f"{employee.get('employee_id', '')}"
    )


def build_employee_options(employees):
    return {
        employee_option_label(employee): employee["employee_id"]
        for employee in employees
    }


def render_section(kicker, title):
    st.markdown(
        f"""
        <div class="section-kicker">{escape(kicker)}</div>
        <div class="section-title">{escape(title)}</div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state(title, message):
    st.markdown(
        f"""
        <div class="empty-state">
            <div class="empty-title">{escape(title)}</div>
            <div>{escape(message)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_error_state(title, message):
    st.markdown(
        f"""
        <div class="error-box">
            <strong>{escape(title)}</strong>
            <br />
            {escape(message)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_latest_joining(employees):
    dates = [employee.get("joining_date") for employee in employees if employee.get("joining_date")]
    return max(dates) if dates else "—"


def render_metric_strip(employees, approvals):
    status_counts = Counter(employee.get("onboarding_status") for employee in employees)
    pending = status_counts.get("PENDING", 0)
    ready = status_counts.get("PLAN_READY", 0)
    awaiting = sum(
        1
        for approval in approvals
        if approval.get("approval_status") == "Awaiting Approval"
    )
    open_tasks_label = "Use Ops"
    latest_joining = get_latest_joining(employees)
    selected_metric = st.session_state.get("selected_metric", "Employees")
    metrics = [
        ("Employees", len(employees), "Directory records"),
        ("Pending Plans", pending, "Need plan generation"),
        ("Plans Ready", ready, "Ready for execution"),
        ("Latest Joining", latest_joining, "Newest start date"),
        ("Approval Queue", awaiting, "Waiting for review"),
        ("Open Tasks", open_tasks_label, "Tracked in Operations"),
    ]

    metric_markup = []
    for label, value, help_text in metrics:
        active_class = " metric-tile-active" if selected_metric == label else ""
        metric_markup.append(
            (
                f'<div class="metric-tile{active_class}">'
                f'<div class="metric-label">{escape(label)}</div>'
                f'<div class="metric-value">{escape(str(value))}</div>'
                f'<div class="metric-help">{escape(help_text)}</div>'
                "</div>"
            )
        )

    st.markdown(
        f'<div class="metric-strip">{"".join(metric_markup)}</div>',
        unsafe_allow_html=True,
    )

    metric_columns = st.columns(6)
    for column, (label, _value, _help_text) in zip(metric_columns, metrics):
        with column:
            if st.button(
                f"View {label}",
                key=f"metric_{label}",
                use_container_width=True,
            ):
                st.session_state["selected_metric"] = label


def render_employee_panel(employee, action_label=None, action_key=None):
    status = format_status(employee.get("onboarding_status"))
    status_class = chip_class_for_status(status)
    st.markdown(
        f"""
        <div class="employee-panel">
            <div class="employee-row">
                <div>
                    <div class="employee-name">{escape(employee.get("employee_name", "Unknown employee"))}</div>
                    <div class="employee-meta">
                        {escape(employee.get("role", "Role not set"))} · {escape(employee.get("department", "Department not set"))}
                        <br />
                        {escape(employee.get("employee_email", ""))}
                    </div>
                </div>
                <span class="chip {status_class}">{escape(status)}</span>
            </div>
            <div class="chip-row">
                <span class="chip">{escape(employee.get("employee_id", ""))}</span>
                <span class="chip">Joining {escape(employee.get("joining_date", "Not set"))}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if action_label and action_key:
        if st.button(
            action_label,
            key=action_key,
            use_container_width=True,
        ):
            st.session_state["workspace_employee_id"] = employee["employee_id"]
            st.session_state["selected_metric"] = "Employees"


def render_task_card(task, enforcement=None):
    priority = str(task.get("task_priority", "Medium")).lower()
    priority_class = {
        "high": "chip-high",
        "medium": "chip-medium",
        "low": "chip-low",
    }.get(priority, "")
    approval_label = "Approval required" if task.get("approval_required") else "No approval"
    status_class = chip_class_for_status(task.get("task_status"))
    lock_chip = ""
    card_state_class = ""
    if enforcement:
        if enforcement.get("is_locked"):
            lock_chip = '<span class="chip chip-locked">Locked</span>'
            card_state_class = " task-card-locked"
        else:
            lock_chip = '<span class="chip chip-unlocked">Unlocked</span>'
            card_state_class = " task-card-ready"

    st.markdown(
        f"""
        <div class="task-card{card_state_class}">
            <div class="task-title-row">
                <div class="task-title">{escape(task.get("task_name", "Untitled task"))}</div>
                <span class="chip {status_class}">{escape(format_status(task.get("task_status")))}</span>
            </div>
            <div class="task-description">{escape(task.get("task_description", "No description provided."))}</div>
            <div class="chip-row">
                <span class="chip {priority_class}">{escape(str(task.get("task_priority", "Medium")))}</span>
                <span class="chip">Owner: {escape(str(task.get("assigned_owner", "Unassigned")))}</span>
                <span class="chip">{approval_label}</span>
                {lock_chip}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_tasks(data):
    tasks = data.get("tasks", [])
    if not tasks:
        render_empty_state(
            "No tasks yet",
            "Generate an onboarding plan to create task work items.",
        )
        return

    total = data.get("task_count", len(tasks))
    approvals = data.get(
        "approval_required_count",
        sum(1 for task in tasks if task.get("approval_required")),
    )
    high_priority = sum(1 for task in tasks if task.get("task_priority") == "High")

    st.markdown(
        f"""
        <div class="metric-strip">
            <div class="metric-tile">
                <div class="metric-label">Tasks</div>
                <div class="metric-value">{total}</div>
            </div>
            <div class="metric-tile">
                <div class="metric-label">High Priority</div>
                <div class="metric-value">{high_priority}</div>
            </div>
            <div class="metric-tile">
                <div class="metric-label">Needs Approval</div>
                <div class="metric-value">{approvals}</div>
            </div>
            <div class="metric-tile">
                <div class="metric-label">Pending Reviews</div>
                <div class="metric-value">{data.get("pending_approval_count", 0)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for task in tasks:
        enforcement = None
        dependency_data = None
        dependency_error = None
        if task.get("task_id"):
            dependency_data, dependency_error = fetch_task_dependencies(task["task_id"])
            enforcement = dependency_data.get("enforcement", {}) if dependency_data else {}
        render_task_card(task, enforcement=enforcement)
        if dependency_error:
            st.caption(f"Dependency state unavailable: {dependency_error}")
        elif dependency_data:
            render_dependency_summary(task, data=dependency_data)


def render_approval_card(approval):
    status = approval.get("approval_status", "Awaiting Approval")
    status_class = chip_class_for_status(status)
    st.markdown(
        f"""
        <div class="task-card">
            <div class="task-title-row">
                <div class="task-title">{escape(approval.get("action_type", "Approval request"))}</div>
                <span class="chip {status_class}">{escape(status)}</span>
            </div>
            <div class="task-description">
                Employee: {escape(approval.get("employee_id", ""))}
                <br />
                Task: {escape(approval.get("related_task_id", "Unlinked"))}
            </div>
            <div class="chip-row">
                <span class="chip">Reviewed by: {escape(approval.get("reviewed_by") or "Not reviewed")}</span>
                <span class="chip">Created: {escape(str(approval.get("created_at", ""))[:10])}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dependency_summary(task, data=None, error=None):
    if data is None and error is None:
        data, error = fetch_task_dependencies(task["task_id"])

    if error:
        st.warning(f"Could not load dependencies. {error}")
        return None

    dependencies = data.get("dependencies", [])
    enforcement = data.get("enforcement", {})
    lock_reasons = enforcement.get("lock_reasons", [])
    state_label = "Locked" if enforcement.get("is_locked") else "Unlocked"

    reason_markup = ""
    if lock_reasons:
        reason_markup = "<br />".join(
            f"Blocked by: {escape(reason)}" for reason in lock_reasons
        )
    else:
        reason_markup = "Ready to start."

    if not dependencies:
        st.markdown(
            f"""
            <div class="dependency-state {'dependency-locked' if enforcement.get("is_locked") else 'dependency-ready'}">
                Dependency state: {escape(state_label)}
                <br />
                {reason_markup}
            </div>
            """,
            unsafe_allow_html=True,
        )
        return enforcement

    dependency_lines = []
    for dependency in dependencies:
        status = escape(dependency.get("depends_on_task_status", "Unknown"))
        name = escape(dependency.get("depends_on_task_name", "Upstream task"))
        dependency_lines.append(f"Depends on: {name} ({status})")

    st.markdown(
        f"""
        <div class="dependency-state {'dependency-locked' if enforcement.get("is_locked") else 'dependency-ready'}">
            Dependency state: {escape(state_label)}
            <br />
            {"<br />".join(dependency_lines)}
            <br />
            {reason_markup}
        </div>
        """,
        unsafe_allow_html=True,
    )
    return enforcement


def render_timeline(employee_id):
    data, error = fetch_employee_timeline(employee_id)
    if error:
        st.warning(f"Could not load timeline. {error}")
        return

    events = data.get("events", [])
    if not events:
        render_empty_state(
            "No timeline yet",
            "Workflow events will appear after plans, approvals, or task updates.",
        )
        return

    for event in events[:8]:
        status_class = chip_class_for_status(event.get("event_status", "Success"))
        st.markdown(
            f"""
            <div class="task-card timeline-item">
                <div class="task-title-row">
                    <div class="task-title">{escape(event.get("event_type", "event").replace("_", " ").title())}</div>
                    <span class="chip {status_class}">{escape(event.get("event_status", "Success"))}</span>
                </div>
                <div class="task-description">
                    {escape(event.get("event_message", ""))}
                    <br />
                    {escape(str(event.get("timestamp", ""))[:19])}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_workflow_runs_panel(key_prefix="workflow"):
    workflow_runs, error = fetch_workflow_runs()
    if error:
        render_error_state("Workflow runs unavailable", error)
        return

    render_section("Observability", "Recent Workflow Runs")
    if not workflow_runs:
        render_empty_state(
            "No workflow runs",
            "Workflow executions will appear after generating an onboarding plan.",
        )
        return

    run_options = {
        f"{run['workflow_run_id']} · {run['employee_id']} · {run['workflow_status']}": run[
            "workflow_run_id"
        ]
        for run in workflow_runs
    }
    selected_label = st.selectbox(
        "Workflow run",
        options=list(run_options.keys()),
        key=f"{key_prefix}_workflow_run_select",
    )
    selected_run_id = run_options.get(selected_label)

    if not selected_run_id:
        return

    data, detail_error = fetch_workflow_run(selected_run_id)
    if detail_error:
        render_error_state("Could not load workflow run details", detail_error)
        return

    workflow_run = data.get("workflow_run", {})
    agent_runs = data.get("agent_runs", [])
    status_class = chip_class_for_status(workflow_run.get("workflow_status"))

    st.markdown(
        f"""
        <div class="workflow-card">
            <div class="task-title-row">
                <div class="task-title">{escape(workflow_run.get("workflow_run_id", ""))}</div>
                <span class="chip {status_class}">{escape(workflow_run.get("workflow_status", ""))}</span>
            </div>
            <div class="task-description">
                Employee: {escape(workflow_run.get("employee_id", ""))}
                <br />
                Started: {escape(str(workflow_run.get("started_at", ""))[:19])}
                <br />
                Completed: {escape(str(workflow_run.get("completed_at", ""))[:19])}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not agent_runs:
        render_empty_state(
            "No agent history",
            "Agent execution summaries were not recorded for this workflow run.",
        )
        return

    for agent_run in agent_runs:
        status_class = chip_class_for_status(agent_run.get("execution_status"))
        st.markdown(
            f"""
            <div class="task-card agent-step">
                <div class="task-title-row">
                    <div class="task-title">{escape(agent_run.get("agent_name", ""))}</div>
                    <span class="chip {status_class}">{escape(agent_run.get("execution_status", ""))}</span>
                </div>
                <div class="task-description">
                    Step {escape(str(agent_run.get("execution_order", "")))} ·
                    {escape(agent_run.get("output_summary", ""))}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_create_tab():
    render_section("Employee Setup", "New Employee")
    with st.form("create_employee_form", clear_on_submit=False):
        left, right = st.columns(2)
        with left:
            employee_name = st.text_input("Full name", placeholder="Sarah Chen")
            employee_email = st.text_input(
                "Work email",
                placeholder="sarah.chen@company.com",
            )
            joining_date = st.date_input("Joining date", value=date.today())
        with right:
            role = st.text_input("Role", placeholder="Data Engineer")
            department = st.text_input(
                "Department",
                placeholder="Platform Engineering",
            )

        submitted = st.form_submit_button(
            "Create Employee",
            type="primary",
            use_container_width=True,
        )

    if not submitted:
        return

    required_fields = {
        "name": employee_name,
        "email": employee_email,
        "role": role,
        "department": department,
    }
    missing = [label for label, value in required_fields.items() if not value.strip()]

    if missing:
        st.warning(f"Please fill in: {', '.join(missing)}.")
        return

    payload = {
        "employee_name": employee_name.strip(),
        "employee_email": employee_email.strip(),
        "role": role.strip(),
        "department": department.strip(),
        "joining_date": joining_date.isoformat(),
    }
    data, error = request_api("POST", "/employees", json=payload)

    if error:
        render_error_state("Failed to create employee", error)
        return

    st.cache_data.clear()
    st.success("Employee created successfully.")
    st.code(data["employee_id"], language="text")
    render_employee_panel(data["employee"])


def render_generate_tab(employees):
    render_section("Planning", "Generate Onboarding Plan")
    if not employees:
        render_empty_state(
            "No employees available",
            "Create an employee before generating an onboarding plan.",
        )
    employee_options = build_employee_options(employees)
    selected_label = st.selectbox(
        "Choose an employee",
        options=list(employee_options.keys()),
        index=0 if employee_options else None,
        placeholder="Select an employee",
    )
    manual_employee_id = st.text_input(
        "Or enter employee ID",
        placeholder="EMP_XXXXXXXX",
        key="generate_employee_id",
    )
    selected_employee_id = (
        normalize_employee_id(manual_employee_id)
        or employee_options.get(selected_label, "")
    )

    if st.button("Generate Plan", type="primary", use_container_width=True):
        if not selected_employee_id:
            st.warning("Select an employee or enter an employee ID.")
            return

        with st.spinner("Running onboarding workflow..."):
            data, error = request_api(
                "POST",
                f"/employees/{selected_employee_id}/generate-onboarding-plan",
                timeout=90,
            )

        if error:
            render_error_state("Failed to generate onboarding plan", error)
            return

        st.cache_data.clear()
        st.success("Onboarding plan is ready.")
        st.caption(f"Workflow run: {data.get('workflow_run_id', 'Not recorded')}")
        render_tasks(data)
        with st.expander("Workflow details"):
            st.json(
                {
                    "workflow_status": data.get("workflow_status"),
                    "next_agent": data.get("next_agent"),
                    "routing_reason": data.get("routing_reason"),
                    "agent_outputs": data.get("agent_outputs"),
                    "approval_count": data.get("approval_count"),
                }
            )


def render_tasks_tab(employees):
    render_section("Task Review", "Employee Tasks")
    if not employees:
        render_empty_state(
            "No employees available",
            "Create an employee before reviewing task plans.",
        )
    employee_options = build_employee_options(employees)
    selected_label = st.selectbox(
        "Employee",
        options=list(employee_options.keys()),
        index=0 if employee_options else None,
        placeholder="Select an employee",
        key="task_employee_select",
    )
    task_employee_id_input = st.text_input(
        "Or enter employee ID",
        placeholder="EMP_XXXXXXXX",
        key="task_employee_id",
    )
    task_employee_id = normalize_employee_id(
        task_employee_id_input
    ) or employee_options.get(selected_label, "")

    if st.button("Fetch Tasks", use_container_width=True):
        if not task_employee_id:
            st.warning("Select an employee or enter an employee ID.")
            return

        data, error = fetch_tasks(task_employee_id)
        if error:
            render_error_state("Could not fetch tasks", error)
            return

        employee = data.get("employee")
        if employee:
            render_employee_panel(employee)
        render_tasks(data)


def render_employee_workspace(employees):
    render_section("Workspace", "Employee Operating View")
    if not employees:
        render_empty_state(
            "No employee selected",
            "Create an employee before opening the workspace.",
        )
        return

    employee_options = build_employee_options(employees)
    preferred_employee_id = st.session_state.get("workspace_employee_id", "")
    option_values = list(employee_options.values())
    default_index = (
        option_values.index(preferred_employee_id)
        if preferred_employee_id in option_values
        else 0
    )
    selected_label = st.selectbox(
        "Employee",
        options=list(employee_options.keys()),
        index=default_index,
        key="workspace_employee_select",
    )
    selected_employee_id = employee_options.get(selected_label, "")
    if not selected_employee_id:
        render_empty_state(
            "No employee selected",
            "Select an employee to open their workspace.",
        )
        return

    st.session_state["workspace_employee_id"] = selected_employee_id
    selected_employee = next(
        (
            employee
            for employee in employees
            if employee.get("employee_id") == selected_employee_id
        ),
        None,
    )

    profile_tab, plan_tab, tasks_tab, approvals_tab, timeline_tab = st.tabs(
        ["Profile", "Onboarding Plan", "Tasks", "Approvals", "Workflow"]
    )

    with profile_tab:
        if selected_employee:
            render_employee_panel(selected_employee)
            with st.expander("Edit employee profile"):
                with st.form(f"edit_employee_{selected_employee_id}"):
                    left, right = st.columns(2)
                    with left:
                        employee_name = st.text_input(
                            "Full name",
                            value=selected_employee.get("employee_name", ""),
                        )
                        employee_email = st.text_input(
                            "Work email",
                            value=selected_employee.get("employee_email", ""),
                        )
                        joining_date = st.date_input(
                            "Joining date",
                            value=parse_joining_date(
                                selected_employee.get("joining_date")
                            ),
                        )
                    with right:
                        role = st.text_input(
                            "Role",
                            value=selected_employee.get("role", ""),
                        )
                        department = st.text_input(
                            "Department",
                            value=selected_employee.get("department", ""),
                        )
                    submitted = st.form_submit_button(
                        "Save Profile",
                        type="primary",
                        use_container_width=True,
                    )
                if submitted:
                    payload = {
                        "employee_name": employee_name.strip(),
                        "employee_email": employee_email.strip(),
                        "role": role.strip(),
                        "department": department.strip(),
                        "joining_date": joining_date.isoformat(),
                    }
                    data, error = request_api(
                        "PUT",
                        f"/employees/{selected_employee_id}",
                        json=payload,
                    )
                    if error:
                        render_error_state("Could not save profile", error)
                    else:
                        st.cache_data.clear()
                        st.success("Employee profile saved.")
                        render_employee_panel(data.get("employee", {}))

    with plan_tab:
        if st.button(
            "Generate or Continue Plan",
            type="primary",
            use_container_width=True,
            key=f"workspace_generate_{selected_employee_id}",
        ):
            with st.spinner("Running onboarding workflow..."):
                data, error = request_api(
                    "POST",
                    f"/employees/{selected_employee_id}/generate-onboarding-plan",
                    timeout=90,
                )
            if error:
                render_error_state("Could not generate plan", error)
            else:
                st.cache_data.clear()
                st.success("Onboarding plan is ready.")
                st.caption(f"Workflow run: {data.get('workflow_run_id', 'Not recorded')}")
                render_tasks(data)

    with tasks_tab:
        data, error = fetch_tasks(selected_employee_id)
        if error:
            render_error_state("Could not load tasks", error)
        else:
            render_tasks(data)

    with approvals_tab:
        approvals, error = fetch_approvals()
        if error:
            render_error_state("Could not load approvals", error)
        else:
            employee_approvals = [
                approval
                for approval in approvals
                if approval.get("employee_id") == selected_employee_id
            ]
            if not employee_approvals:
                render_empty_state(
                    "No approvals for this employee",
                    "Approval-required tasks will appear here after plan generation.",
                )
            for approval in employee_approvals:
                render_approval_card(approval)

    with timeline_tab:
        render_timeline(selected_employee_id)
        st.divider()
        render_workflow_runs_panel(key_prefix="workspace")


def render_operations_tab(employees, all_approvals):
    pending_approvals, approval_error = fetch_approvals("Awaiting Approval")
    pending_count = len(pending_approvals)
    reviewed_count = max(len(all_approvals) - pending_count, 0)

    render_section("Operations", "Workflow Command Center")
    st.markdown(
        f"""
        <div class="metric-strip">
            <div class="metric-tile">
                <div class="metric-label">Pending Approvals</div>
                <div class="metric-value">{pending_count}</div>
            </div>
            <div class="metric-tile">
                <div class="metric-label">Reviewed</div>
                <div class="metric-value">{reviewed_count}</div>
            </div>
            <div class="metric-tile">
                <div class="metric-label">Employees</div>
                <div class="metric-value">{len(employees)}</div>
            </div>
            <div class="metric-tile">
                <div class="metric-label">Workflow</div>
                <div class="metric-value">Phase 2</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    approval_column, task_column = st.columns([1, 1], gap="large")

    with approval_column:
        render_section("Human Review", "Approval Queue")
        if approval_error:
            render_error_state("Could not load approvals", approval_error)
        elif not pending_approvals:
            render_empty_state(
                "No approvals waiting",
                "Approval-required tasks will appear here after plan generation.",
            )
        else:
            for approval in pending_approvals:
                render_approval_card(approval)
                notes = st.text_input(
                    "Review notes",
                    key=f"approval_notes_{approval['approval_id']}",
                    placeholder="Optional note",
                )
                decision_columns = st.columns(3)
                decisions = [
                    ("Approve", "Approved", "primary"),
                    ("Reject", "Rejected", "secondary"),
                    ("Request Revision", "Revision Requested", "secondary"),
                ]
                for column, (label, status, button_type) in zip(decision_columns, decisions):
                    with column:
                        if st.button(
                            label,
                            key=f"approval_{status}_{approval['approval_id']}",
                            type=button_type,
                            use_container_width=True,
                        ):
                            payload = {
                                "approval_status": status,
                                "review_notes": notes,
                                "reviewed_by": "HR",
                            }
                            _, error = request_api(
                                "PATCH",
                                f"/approvals/{approval['approval_id']}",
                                json=payload,
                            )
                            if error:
                                render_error_state("Could not save decision", error)
                            else:
                                st.cache_data.clear()
                                st.success("Approval decision saved.")
                                st.rerun()

    with task_column:
        render_section("Execution", "Task Status")
        employee_options = build_employee_options(employees)
        selected_label = st.selectbox(
            "Employee",
            options=list(employee_options.keys()),
            index=0 if employee_options else None,
            placeholder="Select an employee",
            key="operations_employee_select",
        )
        selected_employee_id = employee_options.get(selected_label, "")

        if not selected_employee_id:
            render_empty_state(
                "No employee selected",
                "Select an employee to review tasks, blockers, and status updates.",
            )
            return

        data, error = fetch_tasks(selected_employee_id)
        if error:
            render_error_state("Could not load tasks", error)
            return

        tasks = data.get("tasks", [])
        if not tasks:
            render_empty_state(
                "No tasks found",
                "Generate an onboarding plan before updating task status.",
            )
            return

        valid_statuses = ["Pending", "In Progress", "Completed", "Blocked", "Failed"]
        for task in tasks:
            dependency_data, dependency_error = fetch_task_dependencies(task["task_id"])
            enforcement = dependency_data.get("enforcement", {}) if dependency_data else {}
            render_task_card(task, enforcement=enforcement)
            if dependency_error:
                st.warning(f"Could not load dependencies. {dependency_error}")
            else:
                render_dependency_summary(
                    task,
                    data=dependency_data,
                    error=dependency_error,
                )
            current_status = task.get("task_status", "Pending")
            status_options = valid_statuses
            if enforcement.get("is_locked") and current_status != "In Progress":
                status_options = [
                    option for option in valid_statuses if option != "In Progress"
                ]
            status = st.selectbox(
                "Update status",
                options=status_options,
                index=status_options.index(current_status)
                if current_status in status_options
                else 0,
                key=f"task_status_{task['task_id']}",
            )
            if st.button(
                "Save task status",
                key=f"save_task_status_{task['task_id']}",
                use_container_width=True,
            ):
                _, status_error = request_api(
                    "PATCH",
                    f"/tasks/{task['task_id']}/status",
                    json={"task_status": status},
                )
                if status_error:
                    render_error_state("Could not update task", status_error)
                else:
                    st.cache_data.clear()
                    st.success("Task status updated.")
                    st.rerun()

        render_section("Audit Trail", "Workflow Timeline")
        render_timeline(selected_employee_id)

    st.divider()
    render_workflow_runs_panel(key_prefix="operations")


def render_directory_tab(employees):
    render_section("Directory", "Employee Records")
    if not employees:
        render_empty_state(
            "No employees yet",
            "Create your first employee record to start onboarding operations.",
        )
        return

    for employee in employees:
        render_employee_panel(
            employee,
            action_label="Open Workspace",
            action_key=f"open_workspace_{employee['employee_id']}",
        )


inject_styles()

with st.sidebar:
    st.subheader("Onboarding Buddy")
    st.caption("Workflow Operations MVP")
    health, health_error = request_api("GET", "/health", timeout=5)
    if health_error:
        st.markdown(
            """
            <span class="status-pill status-offline">
                <span class="status-dot" style="background:#b91c1c"></span>
                API offline
            </span>
            """,
            unsafe_allow_html=True,
        )
        with st.expander("Connection details"):
            st.caption(health_error)
    else:
        st.markdown(
            """
            <span class="status-pill status-online">
                <span class="status-dot" style="background:#15803d"></span>
                API online
            </span>
            """,
            unsafe_allow_html=True,
        )
        st.caption(API_BASE_URL)

    if st.button("Refresh data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.markdown(
    """
    <section class="app-header">
        <h1 class="app-title">Onboarding Buddy</h1>
        <p class="app-subtitle">
            Create employee records, generate onboarding plans, review HR approvals, and update onboarding task status from one focused workspace.
        </p>
    </section>
    """,
    unsafe_allow_html=True,
)

employees, employees_error = fetch_employees()
approvals, approvals_error = fetch_approvals()

if employees_error:
    render_error_state("Could not load employees", employees_error)
if approvals_error:
    render_error_state("Could not load approvals", approvals_error)

render_metric_strip(employees, approvals)

tab_workspace, tab_create, tab_generate, tab_tasks, tab_operations, tab_directory = st.tabs(
    ["Workspace", "Create", "Generate Plan", "Tasks", "Operations", "Directory"]
)

with tab_workspace:
    render_employee_workspace(employees)

with tab_create:
    render_create_tab()

with tab_generate:
    render_generate_tab(employees)

with tab_tasks:
    render_tasks_tab(employees)

with tab_operations:
    render_operations_tab(employees, approvals)

with tab_directory:
    render_directory_tab(employees)

st.caption("Onboarding Buddy")
