import requests
import streamlit as st

import streamlit as st

API_BASE_URL = st.secrets.get(
    "API_BASE_URL",
    "http://127.0.0.1:8000"
)

st.set_page_config(
    page_title="Onboarding Buddy",
    page_icon="🤖",
    layout="wide",
)

st.markdown(
    """
    <style>
    .main {
        background-color: #f8fafc;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1100px;
    }
    .hero-card {
        background: linear-gradient(135deg, #111827, #1e3a8a);
        padding: 2rem;
        border-radius: 18px;
        color: white;
        margin-bottom: 2rem;
    }
    .task-card {
        background: #111827;
        color: #f9fafb;
        padding: 1rem;
        border-radius: 12px;
        border-left: 5px solid #2563eb;
        margin-bottom: 0.8rem;
    }
    .task-card h4 {
        color: #ffffff;
        margin-bottom: 0.5rem;
    }
    .task-card p {
        color: #d1d5db;
        margin-bottom: 0.4rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-card">
        <h1>🤖 Onboarding Buddy</h1>
        <p>AI-Powered Employee Onboarding Assistant.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_create, tab_view, tab_tasks = st.tabs(
    ["Create Employee", "Generate Plan", "View Tasks"]
)

with tab_create:
    st.markdown("### Create New Employee")

    with st.form("create_employee_form"):
        employee_name = st.text_input("Employee Name", placeholder="Sarah Chen")
        employee_email = st.text_input("Employee Email", placeholder="sarah.chen@company.com")
        role = st.text_input("Role", placeholder="Data Engineer")
        department = st.text_input("Department", placeholder="Platform Engineering")
        joining_date = st.date_input("Joining Date")

        submitted = st.form_submit_button("Create Employee")

        if submitted:
            payload = {
                "employee_name": employee_name,
                "employee_email": employee_email,
                "role": role,
                "department": department,
                "joining_date": joining_date.isoformat(),
            }

            try:
                response = requests.post(
                    f"{API_BASE_URL}/employees",
                    json=payload,
                    timeout=30,
                )

                if response.status_code == 200:
                    data = response.json()
                    st.success("Employee created successfully.")
                    st.write("Employee ID:")
                    st.code(data["employee_id"])
                    st.json(data)
                else:
                    st.error("Failed to create employee.")
                    st.json(response.json())

            except Exception as error:
                st.error(f"Backend request failed: {error}")

with tab_view:
    st.markdown("### Generate Onboarding Plan")

    employee_id = st.text_input(
        "Employee ID",
        placeholder="EMP_XXXXXXXX",
        key="generate_employee_id",
    )

    if st.button("Generate Onboarding Plan"):
        if not employee_id:
            st.warning("Please enter an employee ID first.")
        else:
            try:
                with st.spinner("Running AI onboarding workflow..."):
                    response = requests.post(
                        f"{API_BASE_URL}/employees/{employee_id}/generate-onboarding-plan",
                        timeout=90,
                    )

                if response.status_code == 200:
                    data = response.json()
                    st.success("Onboarding plan generated successfully.")
                    st.write(f"Generated {data['task_count']} onboarding tasks.")

                    for task in data["tasks"]:
                        st.markdown(
                            f"""
                            <div class="task-card">
                                <h4>{task["task_name"]}</h4>
                                <p>{task["task_description"]}</p>
                                <p>
                                    <b>Status:</b> {task["task_status"]} |
                                    <b>Priority:</b> {task["task_priority"]} |
                                    <b>Owner:</b> {task["assigned_owner"]}
                                </p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    with st.expander("View full workflow response"):
                        st.json(data)

                else:
                    st.error("Failed to generate onboarding plan.")
                    st.json(response.json())

            except Exception as error:
                st.error(f"Backend request failed: {error}")

with tab_tasks:
    st.markdown("### View Onboarding Tasks")

    task_employee_id = st.text_input(
        "Employee ID",
        placeholder="EMP_XXXXXXXX",
        key="task_employee_id",
    )

    if st.button("Fetch Tasks"):
        if not task_employee_id:
            st.warning("Please enter an employee ID first.")
        else:
            try:
                response = requests.get(
                    f"{API_BASE_URL}/employees/{task_employee_id}/tasks",
                    timeout=30,
                )

                if response.status_code == 200:
                    data = response.json()
                    st.success(f"Found {data['task_count']} tasks.")

                    for task in data["tasks"]:
                        st.markdown(
                            f"""
                            <div class="task-card">
                                <h4>{task["task_name"]}</h4>
                                <p>{task["task_description"]}</p>
                                <p>
                                    <b>Status:</b> {task["task_status"]} |
                                    <b>Priority:</b> {task["task_priority"]} |
                                    <b>Owner:</b> {task["assigned_owner"]}
                                </p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                else:
                    st.error("Could not fetch tasks.")
                    st.json(response.json())

            except Exception as error:
                st.error(f"Backend request failed: {error}")

st.divider()
st.caption("Onboarding Buddy")
