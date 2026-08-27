from gever.leads.search import DdgsSearchProvider, GeversLeadProfile, SearchFinding


def test_search_finding_normalizes_domain():
    finding=SearchFinding(url=" https://example.com/post/1 ",title=" Painter needed ",snippet=" Need interior painting ")
    assert finding.url=="https://example.com/post/1"; assert finding.domain=="example.com"


def test_gevers_queries_are_local_and_buyer_intent_focused():
    queries=GeversLeadProfile().queries()
    joined=" | ".join(queries).lower()
    assert "myrtle beach" in joined and "horry county" in joined
    assert "looking for painter" in joined
    assert "need painter" in joined
    assert len(queries) <= 8
    assert '"interior painting" "myrtle beach"' not in joined
    assert '"commercial painting" "horry county"' not in joined


def test_ddgs_provider_normalizes_results_without_network():
    class FakeDDGS:
        def text(self, query, **kwargs):
            return [{"href":"https://example.com/lead","title":"Painter needed Myrtle Beach","body":"Need painting quote today"},{"title":"bad"}]
    provider=DdgsSearchProvider(ddgs_factory=FakeDDGS)
    results=provider.search("painter Myrtle Beach")
    assert len(results)==1; assert results[0].domain=="example.com"; assert "painting quote" in results[0].snippet


def test_ddgs_provider_treats_no_results_as_empty_not_error():
    class EmptyDDGS:
        def text(self, query, **kwargs):
            raise RuntimeError("No results found.")
    provider=DdgsSearchProvider(ddgs_factory=EmptyDDGS)
    assert provider.search("rare query") == []


def test_ddgs_provider_wraps_real_errors():
    class BrokenDDGS:
        def text(self, query, **kwargs): raise OSError("network down")
    try: DdgsSearchProvider(ddgs_factory=BrokenDDGS).search("painter")
    except RuntimeError as exc: assert "DDGS search failed" in str(exc) and "network down" in str(exc)
    else: raise AssertionError("expected RuntimeError")
