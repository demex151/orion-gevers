import sqlite3

from gever.leads import LeadStore
from gever.leads.evaluator import LeadEvaluator
from gever.leads.hunter import LeadHunter
from gever.leads.search import GeversLeadProfile, SearchFinding


class StaticProvider:
    name = "static"

    def __init__(self, findings):
        self.findings = findings

    def search(self, query):
        return list(self.findings)


class BrokenProvider:
    name = "broken"

    def search(self, query):
        raise RuntimeError("provider unavailable")


def _profile():
    profile = GeversLeadProfile()
    profile.queries = lambda: ["one query"]
    return profile


def test_hunter_counts_accepts_rejects_and_persists(tmp_path):
    store = LeadStore(tmp_path / "leads.db")
    profile = _profile()
    findings = [
        SearchFinding(
            url="https://example.com/hot",
            title="Painter needed ASAP Myrtle Beach",
            snippet="Need a painter and painting quote today in Myrtle Beach.",
            public_contact_method="public reply",
        ),
        SearchFinding(
            url="https://example.com/bad",
            title="Need roofer Myrtle Beach",
            snippet="Need a roofing estimate in Myrtle Beach.",
        ),
    ]
    hunter = LeadHunter(store, LeadEvaluator(profile), profile, [StaticProvider(findings)])

    summary = hunter.run()

    assert summary.raw_findings == 2
    assert summary.accepted_leads == 1
    assert summary.rejected_findings == 1
    assert summary.hot_count == 1
    assert summary.ended_at is not None
    assert len(store.list_leads()) == 1

    with sqlite3.connect(store.db_path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM rejected_findings").fetchone()[0] == 1


def test_hunter_merges_duplicate_candidate(tmp_path):
    store = LeadStore(tmp_path / "leads.db")
    profile = _profile()
    finding = SearchFinding(
        url="https://example.com/duplicate",
        title="Painter needed Myrtle Beach",
        snippet="Need a painting estimate in Myrtle Beach.",
    )
    hunter = LeadHunter(store, LeadEvaluator(profile), profile, [StaticProvider([finding])])

    first = hunter.run()
    second = hunter.run()

    assert first.accepted_leads == 1
    assert second.accepted_leads == 1
    assert second.duplicate_merges == 1
    assert len(store.list_leads()) == 1


def test_provider_failure_is_recorded_and_other_provider_continues(tmp_path):
    store = LeadStore(tmp_path / "leads.db")
    profile = _profile()
    finding = SearchFinding(
        url="https://example.com/good",
        title="Painter needed Myrtle Beach",
        snippet="Looking for a painter and painting quote in Myrtle Beach.",
    )
    hunter = LeadHunter(
        store,
        LeadEvaluator(profile),
        profile,
        [BrokenProvider(), StaticProvider([finding])],
    )

    summary = hunter.run()

    assert summary.accepted_leads == 1
    assert "broken" in summary.errors
    assert "provider unavailable" in summary.errors["broken"]
    assert summary.ended_at is not None
