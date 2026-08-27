import io
import json

import pytest

from gever.leads.search import GeversLeadProfile, JsonSearchProvider, SearchFinding


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


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return io.BytesIO(json.dumps(self.payload).encode("utf-8"))

    def __exit__(self, exc_type, exc, tb):
        return False


def test_json_provider_normalizes_public_results_and_skips_malformed_rows():
    seen = {}

    def opener(request, timeout):
        seen["url"] = request.full_url
        seen["authorization"] = request.headers.get("Authorization")
        seen["timeout"] = timeout
        return FakeResponse({"results": [
            {"url": "https://example.com/lead", "title": "Painter needed", "snippet": "Myrtle Beach painting quote"},
            {"title": "missing url"},
            "junk",
        ]})

    provider = JsonSearchProvider("https://search.example/api", api_key="secret", timeout=7, opener=opener)
    findings = provider.search("painting quote Myrtle Beach")

    assert len(findings) == 1
    assert findings[0].domain == "example.com"
    assert "q=painting+quote+Myrtle+Beach" in seen["url"]
    assert seen["authorization"] == "Bearer secret"
    assert seen["timeout"] == 7


def test_json_provider_raises_useful_error():
    def opener(request, timeout):
        raise OSError("network down")

    provider = JsonSearchProvider("https://search.example/api", opener=opener)
    with pytest.raises(RuntimeError, match="public search failed.*network down"):
        provider.search("painter")
