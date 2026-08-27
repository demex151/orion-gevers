from types import SimpleNamespace

import run_lead_hunter


def test_main_fails_cleanly_without_search_endpoint(monkeypatch, capsys, tmp_path):
    monkeypatch.delenv("GEVER_SEARCH_ENDPOINT", raising=False)
    monkeypatch.setenv("GEVER_LEADS_DB", str(tmp_path / "leads.db"))

    code = run_lead_hunter.main()

    assert code == 2
    assert "GEVER_SEARCH_ENDPOINT" in capsys.readouterr().err
    assert not (tmp_path / "leads.db").exists()


def test_main_prints_compact_hunt_summary(monkeypatch, capsys, tmp_path):
    monkeypatch.setenv("GEVER_SEARCH_ENDPOINT", "https://search.example/api")
    monkeypatch.setenv("GEVER_LEADS_DB", str(tmp_path / "leads.db"))

    fake_summary = SimpleNamespace(
        raw_findings=3,
        accepted_leads=2,
        rejected_findings=1,
        duplicate_merges=0,
        hot_count=1,
        warm_count=1,
        prospect_count=0,
        errors={},
    )
    fake_leads = [SimpleNamespace(
        classification=SimpleNamespace(value="HOT"),
        score=90,
        evidence="Need painter ASAP in Myrtle Beach",
        source_url="https://example.com/lead",
    )]

    class FakeHunter:
        def run(self):
            return fake_summary

    class FakeStore:
        def list_leads(self, limit=20):
            return fake_leads

    monkeypatch.setattr(run_lead_hunter, "build_hunter", lambda endpoint, api_key, db_path: (FakeHunter(), FakeStore()))

    code = run_lead_hunter.main()
    output = capsys.readouterr().out

    assert code == 0
    assert "HOT: 1" in output
    assert "Aceptados: 2" in output
    assert "Need painter ASAP" in output
    assert "https://example.com/lead" in output
