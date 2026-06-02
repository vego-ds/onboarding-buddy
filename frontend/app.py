from collections import Counter
from datetime import date
from html import escape

import requests
import streamlit as st

API_BASE_URL = "http://127.0.0.1:8000"
REQUEST_TIMEOUT = 30

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
            max-width: 760px;
        }
        .metric-strip {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.75rem;
            margin: 0.25rem 0 1rem;
        }
        .metric-tile {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
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
        .task-card,
        .empty-state {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
        }
        .employee-panel {
            padding: 1rem;
            margin-bottom: 0.75rem;
        }
        .employee-name {
            color: var(--ink);
            font-size: 1rem;
            font-weight: 740;
            margin-bottom: 0.15rem;
        }
        .employee-meta {
            color: var(--muted);
            font-size: 0.88rem;
            line-height: 1.45;
        }
        .task-card {
            padding: 1rem;
            margin-bottom: 0.75rem;
        }
        .task-title-row {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 0.35rem;
        }
        .task-title {
            color: var(--ink);
            font-size: 1rem;
            font-weight: 740;
            line-height: 1.35;
        }
        .task-description {
            color: var(--muted);
            font-size: 0.9rem;
            line-height: 1.45;
            margin-bottom: 0.65rem;
        }
        .chip-row {
            display: flex;
            gap: 0.45rem;
            flex-wrap: wrap;
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
        div[data-testid="stForm"] {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 1rem;
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
        .stTextInput input::placeholder {
            color: #7c8794;
            opacity: 1;
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


def fetch_tasks(employee_id):
    return request_api("GET", f"/employees/{employee_id}/tasks")


def format_status(status):
    return str(status or "Unknown").replace("_", " ").title()


def normalize_employee_id(employee_id):
    return employee_id.strip().upper()


def parse_joining_date(joining_date):
    try:
        return date.fromisoformat(joining_date)
    except (TypeError, ValueError):
        return date.today()


def open_dashboard_view(view_name, employees, employee_id=None):
    st.session_state.dashboard_view = view_name

    if employee_id:
        st.session_state.selected_employee_id = employee_id
        return

    matching_employees = get_dashboard_employees(view_name, employees)
    if matching_employees:
        st.session_state.selected_employee_id = matching_employees[0]["employee_id"]


def get_dashboard_employees(view_name, employees):
    if view_name == "pending":
        return [
            employee
            for employee in employees
            if employee.get("onboarding_status") == "PENDING"
        ]

    if view_name == "ready":
        return [
            employee
            for employee in employees
            if employee.get("onboarding_status") == "PLAN_READY"
        ]

    if view_name == "latest":
        latest_joining = max(
            [
                employee.get("joining_date")
                for employee in employees
                if employee.get("joining_date")
            ],
            default=None,
        )
        return [
            employee
            for employee in employees
            if employee.get("joining_date") == latest_joining
        ]

    if view_name == "employee":
        selected_id = st.session_state.get("selected_employee_id")
        return [
            employee
            for employee in employees
            if employee.get("employee_id") == selected_id
        ]

    return employees


def render_metric_strip(employees):
    status_counts = Counter(employee.get("onboarding_status") for employee in employees)
    pending = status_counts.get("PENDING", 0)
    ready = status_counts.get("PLAN_READY", 0)
    latest_joining = max(
        [employee.get("joining_date") for employee in employees if employee.get("joining_date")],
        default="No records",
    )

    metric_columns = st.columns(4)
    metrics = [
        ("Employees", len(employees), "all"),
        ("Pending Plans", pending, "pending"),
        ("Plans Ready", ready, "ready"),
        ("Latest Joining", latest_joining, "latest"),
    ]

    for column, (label, value, view_name) in zip(metric_columns, metrics):
        with column:
            if st.button(
                f"{label}\n\n{value}",
                key=f"metric_{view_name}",
                use_container_width=True,
            ):
                open_dashboard_view(view_name, employees)
                st.rerun()


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


def render_employee_open_button(employee, key_prefix):
    if st.button(
        "Open employee",
        key=f"{key_prefix}_{employee['employee_id']}",
        use_container_width=True,
    ):
        open_dashboard_view("employee", [], employee["employee_id"])
        st.rerun()


def render_employee_workspace(employees):
    view_name = st.session_state.get("dashboard_view")
    if not view_name:
        return

    matching_employees = get_dashboard_employees(view_name, employees)
    selected_id = st.session_state.get("selected_employee_id")
    selected_employee = next(
        (
            employee
            for employee in employees
            if employee.get("employee_id") == selected_id
        ),
        None,
    )

    if matching_employees and selected_employee is None:
        selected_employee = matching_employees[0]
        st.session_state.selected_employee_id = selected_employee["employee_id"]

    view_labels = {
        "all": "All Employees",
        "pending": "Pending Plans",
        "ready": "Plans Ready",
        "latest": "Latest Joining",
        "employee": "Employee Details",
    }

    st.divider()
    st.subheader(view_labels.get(view_name, "Employee Details"))

    if not matching_employees:
        st.markdown(
            '<div class="empty-state">No employees match this dashboard view.</div>',
            unsafe_allow_html=True,
        )
        return

    list_column, detail_column = st.columns([0.9, 1.4], gap="large")

    with list_column:
        st.markdown(f"**{len(matching_employees)} record(s)**")
        for employee in matching_employees:
            render_employee_panel(employee)
            if st.button(
                "Edit / continue",
                key=f"workspace_pick_{view_name}_{employee['employee_id']}",
                use_container_width=True,
            ):
                st.session_state.selected_employee_id = employee["employee_id"]
                st.rerun()

    with detail_column:
        if selected_employee is None:
            return

        render_employee_panel(selected_employee)

        with st.form(
            f"edit_employee_form_{selected_employee['employee_id']}",
            clear_on_submit=False,
        ):
            edit_name = st.text_input(
                "Full name",
                value=selected_employee.get("employee_name", ""),
            )
            edit_email = st.text_input(
                "Work email",
                value=selected_employee.get("employee_email", ""),
            )
            edit_role = st.text_input(
                "Role",
                value=selected_employee.get("role", ""),
            )
            edit_department = st.text_input(
                "Department",
                value=selected_employee.get("department", ""),
            )
            edit_joining_date = st.date_input(
                "Joining date",
                value=parse_joining_date(selected_employee.get("joining_date")),
            )

            update_submitted = st.form_submit_button(
                "Save Changes",
                type="primary",
                use_container_width=True,
            )

        if update_submitted:
            payload = {
                "employee_name": edit_name.strip(),
                "employee_email": edit_email.strip(),
                "role": edit_role.strip(),
                "department": edit_department.strip(),
                "joining_date": edit_joining_date.isoformat(),
            }
            data, error = request_api(
                "PUT",
                f"/employees/{selected_employee['employee_id']}",
                json=payload,
            )

            if error:
                st.error(f"Could not update employee. {error}")
            else:
                st.cache_data.clear()
                st.success(data.get("message", "Employee updated."))
                st.rerun()

        action_columns = st.columns(2)

        with action_columns[0]:
            if st.button(
                "Generate / Continue Plan",
                key=f"workspace_generate_{selected_employee['employee_id']}",
                type="primary",
                use_container_width=True,
            ):
                with st.spinner("Running onboarding workflow..."):
                    data, error = request_api(
                        "POST",
                        f"/employees/{selected_employee['employee_id']}/generate-onboarding-plan",
                        timeout=90,
                    )
                if error:
                    st.error(f"Could not continue plan. {error}")
                else:
                    st.cache_data.clear()
                    st.success("Onboarding workflow updated.")
                    render_tasks(data)

        with action_columns[1]:
            if st.button(
                "View Tasks",
                key=f"workspace_tasks_{selected_employee['employee_id']}",
                use_container_width=True,
            ):
                data, error = fetch_tasks(selected_employee["employee_id"])
                if error:
                    st.error(f"Could not fetch tasks. {error}")
                else:
                    render_tasks(data)


def render_task_card(task):
    priority = str(task.get("task_priority", "Medium")).lower()
    priority_class = {
        "high": "chip-high",
        "medium": "chip-medium",
        "low": "chip-low",
    }.get(priority, "")
    approval_label = "Approval required" if task.get("approval_required") else "No approval"

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
    owners = len({task.get("assigned_owner", "Unassigned") for task in tasks})
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
                <div class="metric-label">Owners</div>
                <div class="metric-value">{owners}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for task in tasks:
        render_task_card(task)


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
            Create employee records, generate onboarding plans, and review task ownership from one focused workspace.
        </p>
    </section>
    """,
    unsafe_allow_html=True,
)

employees, employees_error = fetch_employees()
if employees_error:
    st.warning(f"Could not load recent employees. {employees_error}")

render_metric_strip(employees)
render_employee_workspace(employees)

tab_create, tab_generate, tab_tasks, tab_directory = st.tabs(
    ["Create", "Generate Plan", "Tasks", "Directory"]
)

employee_options = {
    f"{employee['employee_name']} · {employee['employee_id']}": employee["employee_id"]
    for employee in employees
}

with tab_create:
    left, right = st.columns([1.1, 0.9], gap="large")

    with left:
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

        if submitted:
            required_fields = {
                "name": employee_name,
                "email": employee_email,
                "role": role,
                "department": department,
            }
            missing = [label for label, value in required_fields.items() if not value.strip()]

            if missing:
                st.warning(f"Please fill in: {', '.join(missing)}.")
            else:
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
                else:
                    st.cache_data.clear()
                    employee = data["employee"]
                    open_dashboard_view("employee", [], employee["employee_id"])
                    st.success("Employee created successfully.")
                    st.code(employee["employee_id"], language="text")
                    render_employee_panel(employee)

    with right:
        st.subheader("Recent Employees")
        if employees:
            for employee in employees[:5]:
                render_employee_panel(employee)
                render_employee_open_button(employee, "recent_open")
        else:
            st.markdown(
                '<div class="empty-state">Create the first employee to start building onboarding plans.</div>',
                unsafe_allow_html=True,
            )

with tab_generate:
    st.subheader("Generate Onboarding Plan")
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
        else:
            with st.spinner("Running onboarding workflow..."):
                data, error = request_api(
                    "POST",
                    f"/employees/{selected_employee_id}/generate-onboarding-plan",
                    timeout=90,
                )

            if error:
                st.error(f"Failed to generate onboarding plan. {error}")
            else:
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
                        }
                    )

with tab_tasks:
    st.subheader("Task Review")
    task_label = st.selectbox(
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
    ) or employee_options.get(task_label, "")

    if st.button("Fetch Tasks", use_container_width=True):
        if not task_employee_id:
            st.warning("Select an employee or enter an employee ID.")
        else:
            data, error = fetch_tasks(task_employee_id)
            if error:
                st.error(f"Could not fetch tasks. {error}")
            else:
                employee = data.get("employee")
                if employee:
                    render_employee_panel(employee)
                render_tasks(data)

with tab_directory:
    st.subheader("Employee Directory")
    if employees:
        for employee in employees:
            render_employee_panel(employee)
            render_employee_open_button(employee, "directory_open")
    else:
        st.markdown(
            '<div class="empty-state">No employees have been created yet.</div>',
            unsafe_allow_html=True,
        )

st.caption("Onboarding Buddy")
