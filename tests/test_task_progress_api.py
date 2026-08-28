from fastapi import FastAPI
from fastapi.testclient import TestClient

from gever.tasks.api import create_task_router
from gever.tasks.models import Capability
from gever.tasks.runtime import TaskRuntime


def test_progress_endpoint_returns_task_states_without_result_content():
    class Echo(Capability):
        name = "echo"
        def execute(self, context):
            return context
        def verify(self, result):
            return True
    runtime = TaskRuntime()
    app = FastAPI()
    app.include_router(create_task_router(runtime))
    with TestClient(app) as client:
        assert client.get("/api/tasks/progress").json() == {"ok": True, "events": []}
        outcome = runtime.run(Echo(), "private customer data")
        response = client.get("/api/tasks/progress")
        assert response.status_code == 200
        assert response.json()["events"][-1]["task_id"] == outcome.task_id
        assert response.json()["events"][-1]["status"] == "completed"
        assert "private customer data" not in response.text
