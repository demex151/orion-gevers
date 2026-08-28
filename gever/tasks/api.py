"""Read-only task telemetry; does not expose task inputs or result payloads."""

from fastapi import APIRouter


def create_task_router(runtime):
    router = APIRouter()

    @router.get("/api/tasks/progress")
    def task_progress():
        return {"ok": True, "events": runtime.progress_snapshot()}

    return router
