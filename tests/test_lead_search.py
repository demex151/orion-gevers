from gever.leads.search import GeversLeadProfile, SearchFinding


def test_search_finding_normalizes_text_and_domain():
    finding = SearchFinding(
        url=" https://example.com/post/1 ",
        title=" Painter needed ",
        snippet=" Need interior painting ",
    )

    assert finding.url == "https://example.com/post/1"
    assert finding.title == "Painter needed"
    assert finding.snippet == "Need interior painting"
    assert finding.domain == "example.com"


def test_gevers_profile_generates_local_painting_queries():
    profile = GeversLeadProfile()
    queries = profile.queries()
    joined = " | ".join(queries).lower()

    assert queries
    assert "myrtle beach" in joined
    assert "horry county" in joined
    assert "interior painting" in joined
    assert "exterior painting" in joined
    assert "cabinet" in joined
