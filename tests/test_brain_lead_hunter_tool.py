from types import SimpleNamespace

from gever.brain import GeversBrain


class FakeLeadHunter:
    def __init__(self, report):
        self.report = report
        self.calls = 0

    def run_once(self):
        self.calls += 1
        return self.report


class FailingLLM:
    def ask(self, prompt):
        raise AssertionError("NVIDIA conversational LLM should not be called for an explicit Lead Hunter command")


class FakeMemory:
    def remember(self, *args, **kwargs):
        return None

    def context_for(self, *args, **kwargs):
        return ""


def make_brain(hunter):
    brain = GeversBrain.__new__(GeversBrain)
    brain.llm = FailingLLM()
    brain.memory = FakeMemory()
    brain.lead_hunter = hunter
    return brain


def test_spanish_search_clients_command_executes_lead_hunter():
    report = SimpleNamespace(found=21, accepted=0, rejected=21, hot=0, warm=0, prospect=0, errors=[])
    hunter = FakeLeadHunter(report)
    brain = make_brain(hunter)

    response = brain.think("GEVER, busca oportunidades de clientes para Gevers Painting")

    assert hunter.calls == 1
    assert "21" in response
    assert "ninguna oportunidad" in response.lower() or "0 oportunidades" in response.lower()


def test_spanish_find_leads_command_executes_lead_hunter_and_reports_results():
    report = SimpleNamespace(found=12, accepted=2, rejected=10, hot=2, warm=0, prospect=0, errors=[])
    hunter = FakeLeadHunter(report)
    brain = make_brain(hunter)

    response = brain.think("busca clientes de pintura")

    assert hunter.calls == 1
    assert "2" in response
    assert "oportunidades" in response.lower()
