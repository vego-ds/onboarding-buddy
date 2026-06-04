from fastapi import FastAPI

from backend.routes.approvals import router as approvals_router
from backend.routes.assistant import router as assistant_router
from backend.routes.auth import router as auth_router
from backend.routes.employees import router as employees_router
from backend.routes.tasks import router as tasks_router
from backend.routes.workflows import router as workflows_router
from database.db import init_db

app = FastAPI(
    title="Onboarding Buddy API",
    version="0.1.0",
    description="Supervisor-based multi-agent onboarding workflow backend",
)

init_db()

app.include_router(employees_router)
app.include_router(approvals_router)
app.include_router(tasks_router)
app.include_router(workflows_router)
app.include_router(assistant_router)
app.include_router(auth_router)


@app.get("/")
def root():
    return {
        "app": "Onboarding Buddy",
        "status": "running",
        "phase": "Phase 4 - Authentication and RBAC Foundation",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
