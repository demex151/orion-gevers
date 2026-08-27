from types import SimpleNamespace

from gever.brain import GeversBrain


class FakeLeadHunter:
    def __init__(self, report):
        self.report = report
        self.calls = 0

    def run(self, trigger="manual"):
        self.calls += 1
        return self.report


class FailingLLM:
    def ask(self, prompt):
        raise AssertionError("NVIDIA conversational LLM should not be called for an explicit Lead Hunter command")


class FakeMemory:
    def remember(self, *args, **kwargs):
        return None

    def get_context(self, *args, **kwargs):
        return ""


def make_brain(hunter):
    brain = GeversBrain.__new__(GeversBrain)
    brain.llm = FailingLLM()
    brain.memory = FakeMemory()
    brain.messages = [{"role": "system", "content": "test"}]
    brain.lead_hunter = hunter
    return brain


def test_spanish_search_clients_command_executes_lead_hunter():
    report = SimpleNamespace(raw_findings=21, accepted_leads=0, rejected_findings=21, hot_count=0, warm_count=0, prospect_count=0, errors={})
    hunter = FakeLeadHunter(report)
    brain = make_brain(hunter)

    response = brain.think("GEVER, busca oportunidades de clientes para Gevers Painting")

    assert hunter.calls == 1
    assert "21" in response
    assert "ninguna oportunidad" in response.lower() or "0 oportunidades" in response.lower()


def test_spanish_find_leads_command_executes_lead_hunter_and_reports_results():
    report = SimpleNamespace(raw_findings=12, accepted_leads=2, rejected_findings=10, hot_count=2, warm_count=0, prospect_count=0, errors={})
    hunter = FakeLeadHunter(report)
    brain = make_brain(hunter)

    response = brain.think("busca clientes de pintura")

    assert hunter.calls == 1
    assert "2" in response
    assert "oportunidades" in response.lower()
