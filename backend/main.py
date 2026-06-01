from fastapi import FastAPI

from backend.routes.employees import router as employees_router
from database.db import init_db

app = FastAPI(
    title="Onboarding Buddy API",
    version="0.1.0",
    description="Supervisor-based multi-agent onboarding workflow backend",
)

init_db()

app.include_router(employees_router)


@app.get("/")
def root():
    return {
        "app": "Onboarding Buddy",
        "status": "running",
        "phase": "Phase 1 - Engineering Foundation",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
