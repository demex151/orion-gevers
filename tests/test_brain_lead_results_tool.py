from types import SimpleNamespace
from gever.brain import GeversBrain

class FakeStore:
    def latest_run(self):
        return {"raw_findings":36,"accepted_leads":3,"rejected_findings":33,"duplicate_merges":0,"hot_count":3,"warm_count":0,"prospect_count":0}
    def list_leads(self):
        return [SimpleNamespace(classification=SimpleNamespace(value="HOT"),score=91,name="Ana",location="Myrtle Beach",service_requested_or_inferred="interior painting",evidence="Looking for a painter this week",source_url="https://example.com/a")]

class FailingLLM:
    def ask(self,prompt): raise AssertionError

class FakeMemory:
    def get_context(self,*a,**k): return ""

def make_brain():
    brain=GeversBrain.__new__(GeversBrain); brain.llm=FailingLLM(); brain.memory=FakeMemory(); brain.messages=[{"role":"system","content":"test"}]; brain.lead_hunter=None; brain.lead_store=FakeStore(); return brain

def test_summary_followup_reads_stored_results_without_new_search():
    brain=make_brain(); response=brain.think("dame un resumen de lo que encontraste en la búsqueda de clientes")
    assert "36" in response and "3" in response and "HOT" in response

def test_show_clients_followup_reads_actual_saved_lead():
    brain=make_brain(); response=brain.think("muéstrame los clientes que encontraste")
    assert "Ana" in response and "Myrtle Beach" in response and "interior painting" in response
