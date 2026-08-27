from gever.leads.search import DdgsSearchProvider, GeversLeadProfile, SearchFinding

def test_search_finding_normalizes_domain():
    finding=SearchFinding(url=" https://example.com/post/1 ",title=" Painter needed ",snippet=" Need interior painting ")
    assert finding.url=="https://example.com/post/1"; assert finding.domain=="example.com"

def test_gevers_queries_are_local_and_painting_focused():
    joined=" | ".join(GeversLeadProfile().queries()).lower()
    assert "myrtle beach" in joined and "horry county" in joined and "interior painting" in joined and "cabinet" in joined

def test_ddgs_provider_normalizes_results_without_network():
    class FakeDDGS:
        def text(self, query, **kwargs):
            return [{"href":"https://example.com/lead","title":"Painter needed Myrtle Beach","body":"Need painting quote today"},{"title":"bad"}]
    provider=DdgsSearchProvider(ddgs_factory=FakeDDGS)
    results=provider.search("painter Myrtle Beach")
    assert len(results)==1; assert results[0].domain=="example.com"; assert "painting quote" in results[0].snippet

def test_ddgs_provider_wraps_errors():
    class BrokenDDGS:
        def text(self, query, **kwargs): raise OSError("network down")
    try: DdgsSearchProvider(ddgs_factory=BrokenDDGS).search("painter")
    except RuntimeError as exc: assert "DDGS search failed" in str(exc) and "network down" in str(exc)
    else: raise AssertionError("expected RuntimeError")
