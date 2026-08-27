from types import SimpleNamespace

from gever.leads.hunter import LeadHunter
from gever.leads.models import LeadClassification


class Store:
    def __init__(self): self.saved=[]
    def start_run(self, trigger): return SimpleNamespace(run_id="run-1",raw_findings=0,rejected_findings=0,duplicate_merges=0,accepted_leads=0,hot_count=0,warm_count=0,prospect_count=0,errors={})
    def record_rejection(self,*args,**kwargs): pass
    def upsert_lead(self,candidate): self.saved.append(candidate)
    def finish_run(self,summary): pass
    def _connect(self):
        class C:
            def __enter__(self): return self
            def __exit__(self,*a): pass
            def execute(self,*a):
                class R:
                    def fetchone(self): return None
                return R()
        return C()

class Profile:
    def queries(self): return ["painting myrtle beach"]

class Provider:
    name="fake"
    def search(self,q): return [SimpleNamespace(url="https://example.com/1",snippet="need painter",title="Need painter")]

class Evaluator:
    def evaluate(self,finding):
        candidate=SimpleNamespace(dedupe_key="a",classification=LeadClassification.HOT,source_url=finding.url)
        return SimpleNamespace(candidate=candidate,rejection_reason=None)


def test_hunter_emits_real_progress_events_without_changing_summary():
    events=[]
    hunter=LeadHunter(Store(),Evaluator(),Profile(),[Provider()])
    summary=hunter.run(progress_callback=events.append)
    names=[e["type"] for e in events]
    assert names[0]=="started"
    assert "searching" in names
    assert "finding" in names
    assert "accepted" in names
    assert "saved" in names
    assert names[-1]=="completed"
    assert summary.accepted_leads==1
    assert summary.hot_count==1


def test_progress_callback_failure_never_fails_hunt():
    def broken(_event): raise RuntimeError("visual telemetry failed")
    hunter=LeadHunter(Store(),Evaluator(),Profile(),[Provider()])
    summary=hunter.run(progress_callback=broken)
    assert summary.accepted_leads==1
