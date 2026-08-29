import pytest

from gever.leads import LeadStore
from gever.leads.hunter import LeadHunter
from gever.leads.search import GeversLeadProfile, SearchFinding


class StaticProvider:
    name = "static"

    def __init__(self, findings):
        self.findings = findings

    def search(self, query):
        return list(self.findings)


class SingleQueryProfile:
    business_name = "Gevers Painting"
    locations = GeversLeadProfile().locations
    services = GeversLeadProfile().services

    def queries(self):
        return ["one query"]


class BrokenEvaluator:
    """Simulates a real bug in evaluation (not a provider search failure),
    which previously escaped the `finally` block and still got reported
    to telemetry/storage as a normal "completed" run."""

    def evaluate(self, finding):
        raise ValueError("evaluator exploded")


def test_a_real_failure_is_not_reported_as_completed(tmp_path):
    store = LeadStore(tmp_path / "leads.db")
    profile = SingleQueryProfile()
    finding = SearchFinding(url="https://example.com/x", title="Painter needed Myrtle Beach")
    hunter = LeadHunter(store, BrokenEvaluator(), profile, [StaticProvider([finding])])

    events = []
    with pytest.raises(ValueError):
        hunter.run(progress_callback=events.append)

    event_types = [e["type"] for e in events]
    assert "completed" not in event_types
    assert "failed" in event_types

    with_status = store.latest_run_including_failed()
    assert with_status is not None
    assert with_status["status"] == "failed"

    # A failed run must not be surfaced as "the latest search" to the user.
    assert store.latest_run() is None


def test_a_successful_run_is_still_reported_as_completed(tmp_path):
    store = LeadStore(tmp_path / "leads.db")
    profile = SingleQueryProfile()
    finding = SearchFinding(
        url="https://example.com/good",
        title="Painter needed Myrtle Beach",
        snippet="Need a painter and painting quote today in Myrtle Beach.",
    )
    from gever.leads.evaluator import LeadEvaluator
    hunter = LeadHunter(store, LeadEvaluator(profile), profile, [StaticProvider([finding])])

    events = []
    hunter.run(progress_callback=events.append)

    event_types = [e["type"] for e in events]
    assert "completed" in event_types
    assert "failed" not in event_types

    latest = store.latest_run()
    assert latest is not None
    assert latest["status"] == "completed"
