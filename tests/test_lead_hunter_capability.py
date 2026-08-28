from types import SimpleNamespace
import pytest

from gever.tasks.capabilities.lead_hunter import LeadHunterCapability


def report(**changes):
    counts = dict(raw_findings=2, accepted_leads=0, rejected_findings=2,
                  hot_count=0, warm_count=0, prospect_count=0, errors={})
    counts.update(changes)
    return SimpleNamespace(**counts)


@pytest.mark.parametrize("accepted", [0, 2])
def test_runs_hunter_with_existing_telemetry_and_response(accepted):
    events = []
    summary = report(accepted_leads=accepted, rejected_findings=2-accepted, hot_count=accepted)
    class Hunter:
        def run(self, trigger, progress_callback):
            assert trigger == "voice"
            progress_callback({"type": "searching"})
            return summary
    capability = LeadHunterCapability(lambda: (Hunter(), object()), events.append)
    assert capability.execute({}) is summary
    assert events == [{"type": "searching"}]
    assert capability.verify(summary)
    response = capability.format_response(summary)
    assert "Búsqueda completada." in response
    assert ("ninguna oportunidad" if accepted == 0 else "HOT: 2") in response


@pytest.mark.parametrize("summary", [None, SimpleNamespace(), report(raw_findings=-1),
    report(accepted_leads=True), report(hot_count=1), report(errors={"provider": "offline"})])
def test_rejects_invalid_or_incomplete_summary(summary):
    capability = LeadHunterCapability(lambda: (None, None))
    assert not capability.verify(summary)
