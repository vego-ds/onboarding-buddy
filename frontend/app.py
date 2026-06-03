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
            --bg: #f6f7f9;
            --panel: #ffffff;
            --ink: #17202a;
            --muted: #5d6975;
            --line: #d8dee6;
            --accent: #2f6f64;
            --accent-soft: #e4f2ee;
            --blue-soft: #e8f0fb;
            --amber-soft: #fff3d6;
            --danger-soft: #fce8e6;
        }
        .stApp {
            background: var(--bg);
            color: var(--ink);
        }
        .block-container {
            max-width: 1240px;
            padding-top: 1.4rem;
            padding-bottom: 2rem;
        }
        [data-testid="stHeader"] {
            background: transparent;
        }
        .app-header {
            border-bottom: 1px solid var(--line);
            padding: 0.2rem 0 1rem;
            margin-bottom: 1.2rem;
        }
        .app-title {
            font-size: 2.25rem;
            line-height: 1.1;
            font-weight: 760;
            letter-spacing: 0;
            margin: 0;
            color: var(--ink);
        }
        .app-subtitle {
            color: var(--muted);
            font-size: 1rem;
            margin: 0.35rem 0 0;
            max-width: 820px;
        }
        .metric-strip {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.75rem;
            margin: 0.25rem 0 1rem;
        }
        .metric-tile,
        .employee-panel,
        .task-card,
        .empty-state {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
        }
        .metric-tile {
            padding: 0.9rem 1rem;
            min-height: 84px;
        }
        .metric-label {
            color: var(--muted);
            font-size: 0.78rem;
            font-weight: 650;
            text-transform: uppercase;
            margin-bottom: 0.4rem;
        }
        .metric-value {
            color: var(--ink);
            font-size: 1.55rem;
            font-weight: 760;
            line-height: 1.1;
        }
        .employee-panel,
        .task-card {
            padding: 1rem;
            margin-bottom: 0.75rem;
        }
        .employee-name,
        .task-title {
            color: var(--ink);
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
        .chip-row {
            display: flex;
            gap: 0.45rem;
            flex-wrap: wrap;
            margin-top: 0.65rem;
        }
        .chip {
            border-radius: 999px;
            border: 1px solid var(--line);
            color: var(--ink);
            background: #f9fafb;
            font-size: 0.74rem;
            font-weight: 650;
            padding: 0.16rem 0.55rem;
            white-space: nowrap;
        }
        .chip-high { background: var(--danger-soft); }
        .chip-medium { background: var(--amber-soft); }
        .chip-low { background: var(--blue-soft); }
        .chip-status { background: var(--accent-soft); }
        .chip-locked { background: var(--danger-soft); }
        .chip-unlocked { background: var(--accent-soft); }
        .dependency-state {
            border-left: 3px solid var(--line);
            color: var(--muted);
            font-size: 0.86rem;
            line-height: 1.45;
            margin: 0.55rem 0 0.8rem;
            padding-left: 0.75rem;
        }
        .empty-state {
            color: var(--muted);
            padding: 1.1rem;
            margin-top: 0.5rem;
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
            border-radius: 6px;
        }
        .stButton > button,
        .stFormSubmitButton > button {
            background: #ffffff;
            border-radius: 6px;
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


def render_metric_strip(employees, approvals):
    status_counts = Counter(employee.get("onboarding_status") for employee in employees)
    pending = status_counts.get("PENDING", 0)
    ready = status_counts.get("PLAN_READY", 0)
    awaiting = sum(
        1
        for approval in approvals
        if approval.get("approval_status") == "Awaiting Approval"
    )

    st.markdown(
        f"""
        <div class="metric-strip">
            <div class="metric-tile">
                <div class="metric-label">Employees</div>
                <div class="metric-value">{len(employees)}</div>
            </div>
            <div class="metric-tile">
                <div class="metric-label">Pending Plans</div>
                <div class="metric-value">{pending}</div>
            </div>
            <div class="metric-tile">
                <div class="metric-label">Plans Ready</div>
                <div class="metric-value">{ready}</div>
            </div>
            <div class="metric-tile">
                <div class="metric-label">Awaiting Approval</div>
                <div class="metric-value">{awaiting}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_employee_panel(employee):
    st.markdown(
        f"""
        <div class="employee-panel">
            <div class="employee-name">{escape(employee.get("employee_name", "Unknown employee"))}</div>
            <div class="employee-meta">
                {escape(employee.get("employee_id", ""))} · {escape(employee.get("role", ""))}
                · {escape(employee.get("department", ""))}
                <br />
                {escape(employee.get("employee_email", ""))} · Joining {escape(employee.get("joining_date", ""))}
                · {escape(format_status(employee.get("onboarding_status")))}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_task_card(task, enforcement=None):
    priority = str(task.get("task_priority", "Medium")).lower()
    priority_class = {
        "high": "chip-high",
        "medium": "chip-medium",
        "low": "chip-low",
    }.get(priority, "")
    approval_label = "Approval required" if task.get("approval_required") else "No approval"
    lock_chip = ""
    if enforcement:
        if enforcement.get("is_locked"):
            lock_chip = '<span class="chip chip-locked">Locked</span>'
        else:
            lock_chip = '<span class="chip chip-unlocked">Unlocked</span>'

    st.markdown(
        f"""
        <div class="task-card">
            <div class="task-title-row">
                <div class="task-title">{escape(task.get("task_name", "Untitled task"))}</div>
                <span class="chip chip-status">{escape(format_status(task.get("task_status")))}</span>
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
        st.markdown(
            '<div class="empty-state">No onboarding tasks have been generated yet.</div>',
            unsafe_allow_html=True,
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
        render_task_card(task)


def render_approval_card(approval):
    st.markdown(
        f"""
        <div class="task-card">
            <div class="task-title-row">
                <div class="task-title">{escape(approval.get("action_type", "Approval request"))}</div>
                <span class="chip chip-status">{escape(approval.get("approval_status", "Awaiting Approval"))}</span>
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
            <div class="dependency-state">
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
        <div class="dependency-state">
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
        st.markdown(
            '<div class="empty-state">No workflow history has been recorded yet.</div>',
            unsafe_allow_html=True,
        )
        return

    for event in events[:8]:
        st.markdown(
            f"""
            <div class="task-card">
                <div class="task-title-row">
                    <div class="task-title">{escape(event.get("event_type", "event").replace("_", " ").title())}</div>
                    <span class="chip chip-status">{escape(event.get("event_status", "Success"))}</span>
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


def render_workflow_runs_panel():
    workflow_runs, error = fetch_workflow_runs()
    if error:
        st.warning(f"Could not load workflow runs. {error}")
        return

    st.subheader("Recent Workflow Runs")
    if not workflow_runs:
        st.markdown(
            '<div class="empty-state">No workflow runs have been recorded yet.</div>',
            unsafe_allow_html=True,
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
        key="workflow_run_select",
    )
    selected_run_id = run_options.get(selected_label)

    if not selected_run_id:
        return

    data, detail_error = fetch_workflow_run(selected_run_id)
    if detail_error:
        st.warning(f"Could not load workflow run details. {detail_error}")
        return

    workflow_run = data.get("workflow_run", {})
    agent_runs = data.get("agent_runs", [])

    st.markdown(
        f"""
        <div class="task-card">
            <div class="task-title-row">
                <div class="task-title">{escape(workflow_run.get("workflow_run_id", ""))}</div>
                <span class="chip chip-status">{escape(workflow_run.get("workflow_status", ""))}</span>
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

    for agent_run in agent_runs:
        st.markdown(
            f"""
            <div class="task-card">
                <div class="task-title-row">
                    <div class="task-title">{escape(agent_run.get("agent_name", ""))}</div>
                    <span class="chip chip-status">{escape(agent_run.get("execution_status", ""))}</span>
                </div>
                <div class="task-description">
                    {escape(agent_run.get("output_summary", ""))}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_create_tab():
    st.subheader("New Employee")
    with st.form("create_employee_form", clear_on_submit=False):
        employee_name = st.text_input("Full name", placeholder="Sarah Chen")
        employee_email = st.text_input(
            "Work email",
            placeholder="sarah.chen@company.com",
        )
        role = st.text_input("Role", placeholder="Data Engineer")
        department = st.text_input(
            "Department",
            placeholder="Platform Engineering",
        )
        joining_date = st.date_input("Joining date", value=date.today())

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
        st.error(f"Failed to create employee. {error}")
        return

    st.cache_data.clear()
    st.success("Employee created successfully.")
    st.code(data["employee_id"], language="text")
    render_employee_panel(data["employee"])


def render_generate_tab(employees):
    st.subheader("Generate Onboarding Plan")
    employee_options = {
        f"{employee['employee_name']} · {employee['employee_id']}": employee["employee_id"]
        for employee in employees
    }
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
            st.error(f"Failed to generate onboarding plan. {error}")
            return

        st.cache_data.clear()
        st.success("Onboarding plan is ready.")
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
    st.subheader("Task Review")
    employee_options = {
        f"{employee['employee_name']} · {employee['employee_id']}": employee["employee_id"]
        for employee in employees
    }
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
            st.error(f"Could not fetch tasks. {error}")
            return

        employee = data.get("employee")
        if employee:
            render_employee_panel(employee)
        render_tasks(data)


def render_operations_tab(employees, all_approvals):
    pending_approvals, approval_error = fetch_approvals("Awaiting Approval")
    pending_count = len(pending_approvals)
    reviewed_count = max(len(all_approvals) - pending_count, 0)

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
        st.subheader("Approval Queue")
        if approval_error:
            st.error(f"Could not load approvals. {approval_error}")
        elif not pending_approvals:
            st.markdown(
                '<div class="empty-state">No approval requests are waiting for review.</div>',
                unsafe_allow_html=True,
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
                    ("Approve", "Approved"),
                    ("Reject", "Rejected"),
                    ("Revise", "Revision Requested"),
                ]
                for column, (label, status) in zip(decision_columns, decisions):
                    with column:
                        if st.button(
                            label,
                            key=f"approval_{status}_{approval['approval_id']}",
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
                                st.error(f"Could not save decision. {error}")
                            else:
                                st.cache_data.clear()
                                st.success("Approval decision saved.")
                                st.rerun()

    with task_column:
        st.subheader("Task Status")
        employee_options = {
            f"{employee['employee_name']} · {employee['employee_id']}": employee["employee_id"]
            for employee in employees
        }
        selected_label = st.selectbox(
            "Employee",
            options=list(employee_options.keys()),
            index=0 if employee_options else None,
            placeholder="Select an employee",
            key="operations_employee_select",
        )
        selected_employee_id = employee_options.get(selected_label, "")

        if not selected_employee_id:
            st.markdown(
                '<div class="empty-state">Create or select an employee to update task status.</div>',
                unsafe_allow_html=True,
            )
            return

        data, error = fetch_tasks(selected_employee_id)
        if error:
            st.error(f"Could not load tasks. {error}")
            return

        tasks = data.get("tasks", [])
        if not tasks:
            st.markdown(
                '<div class="empty-state">No tasks found for this employee.</div>',
                unsafe_allow_html=True,
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
                    st.error(f"Could not update task. {status_error}")
                else:
                    st.cache_data.clear()
                    st.success("Task status updated.")
                    st.rerun()

        st.subheader("Workflow Timeline")
        render_timeline(selected_employee_id)

    st.divider()
    render_workflow_runs_panel()


def render_directory_tab(employees):
    st.subheader("Employee Directory")
    if not employees:
        st.markdown(
            '<div class="empty-state">No employees have been created yet.</div>',
            unsafe_allow_html=True,
        )
        return

    for employee in employees:
        render_employee_panel(employee)


inject_styles()

with st.sidebar:
    st.subheader("Backend")
    health, health_error = request_api("GET", "/health", timeout=5)
    if health_error:
        st.error("API offline")
        st.caption(health_error)
    else:
        st.success("API online")
        st.caption(f"{API_BASE_URL}")

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
    st.warning(f"Could not load recent employees. {employees_error}")
if approvals_error:
    st.warning(f"Could not load approvals. {approvals_error}")

render_metric_strip(employees, approvals)

tab_create, tab_generate, tab_tasks, tab_operations, tab_directory = st.tabs(
    ["Create", "Generate Plan", "Tasks", "Operations", "Directory"]
)

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
