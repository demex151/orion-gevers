import importlib
import sys
from unittest.mock import patch

from fastapi.testclient import TestClient

from gever.listen import GeversListener
from gever.voice import GeversVoice
from test_memory import make_memory


def load_server_module():
    """Import backend.server without touching a real microphone or the
    system audio mixer. GeversListener/GeversVoice normally open hardware
    in __init__; that is irrelevant to what this test checks (the
    /api/memories route) and would make the test depend on the machine
    it runs on."""
    with patch.object(GeversListener, "__init__", lambda self: None), \
         patch.object(GeversVoice, "__init__", lambda self: None):
        if "backend.server" in sys.modules:
            return importlib.reload(sys.modules["backend.server"])
        return importlib.import_module("backend.server")


def test_memories_endpoint_returns_real_stored_memories(tmp_path):
    server_module = load_server_module()
    # Isolate this test from the developer's real data/memory.json.
    server_module.brain.memory = make_memory(tmp_path)
    server_module.brain.memory.remember("Prueba de auditoria", category="fact")

    with TestClient(server_module.app) as client:
        response = client.get("/api/memories")

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert any(m["content"] == "Prueba de auditoria" for m in body["memories"])


def test_memories_endpoint_does_not_error_when_empty(tmp_path):
    server_module = load_server_module()
    server_module.brain.memory = make_memory(tmp_path)

    with TestClient(server_module.app) as client:
        response = client.get("/api/memories")

    assert response.status_code == 200
    body = response.json()
    assert body == {"ok": True, "memories": []}
