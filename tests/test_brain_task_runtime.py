from types import SimpleNamespace
from unittest.mock import patch

from gever.brain import GeversBrain
from test_brain_lead_hunter_tool import FakeLeadHunter, make_brain


def test_hunter_command_records_verified_runtime_outcome():
    summary = SimpleNamespace(raw_findings=0, accepted_leads=0, rejected_findings=0,
                              hot_count=0, warm_count=0, prospect_count=0, errors={})
    brain = make_brain(FakeLeadHunter(summary))
    assert "Búsqueda completada" in brain.think("ORION, busca clientes")
    assert brain.task_runtime.last_outcome.verified
    assert brain.task_runtime.last_outcome.capability == "lead_hunter"


def test_worker_failure_returns_spanish_error_without_changing_history():
    brain = make_brain(FakeLeadHunter(None))
    history = list(brain.messages)
    response = brain.think("busca clientes")
    assert "No pude completar" in response
    assert "Búsqueda completada" not in response
    assert brain.messages == history


def test_ordinary_conversation_still_calls_nvidia():
    brain = make_brain(FakeLeadHunter(None))
    reply = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="Hola José"))])
    with patch.object(brain, "_analyze_memory_action", return_value={"action": "NONE"}), \
         patch("gever.brain.client.chat.completions.create", return_value=reply) as create:
        assert brain.think("cómo estás hoy") == "Hola José"
    assert create.call_count == 1
    assert brain.task_runtime.last_outcome is None


def test_formatter_failure_does_not_escape_or_repeat_execution():
    from gever.tasks.models import Capability
    class BrokenFormatter(Capability):
        name = "formatter"
        signals = ("ejecuta prueba",)
        def execute(self, context):
            return "done"
        def verify(self, result):
            return result == "done"
        def format_response(self, result):
            raise ValueError("bad formatting")
    brain = make_brain(FakeLeadHunter(None))
    brain._ensure_task_runtime()
    brain.task_registry.register(BrokenFormatter())
    response = brain.think("ejecuta prueba")
    assert "no pude preparar" in response
    assert brain.task_runtime.last_outcome.verified
