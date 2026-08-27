import json
from dataclasses import dataclass
from typing import Protocol
from urllib.parse import urlencode, urlparse, urlsplit, urlunsplit, parse_qsl
from urllib.request import Request, urlopen


@dataclass
class SearchFinding:
    url: str
    title: str = ""
    snippet: str = ""
    domain: str = ""
    published_at: str | None = None
    public_contact_method: str | None = None
    location: str | None = None
    name: str | None = None
    organization: str | None = None

    def __post_init__(self):
        self.url = (self.url or "").strip()
        self.title = (self.title or "").strip()
        self.snippet = (self.snippet or "").strip()
        self.domain = (self.domain or "").strip().lower()
        if not self.domain and self.url:
            self.domain = (urlparse(self.url).hostname or "").lower()
        if self.location is not None:
            self.location = self.location.strip()
        if self.name is not None:
            self.name = self.name.strip()
        if self.organization is not None:
            self.organization = self.organization.strip()


class SearchProvider(Protocol):
    def search(self, query: str) -> list[SearchFinding]: ...


class JsonSearchProvider:
    name = "public_web_search"

    def __init__(self, endpoint: str, api_key: str | None = None, timeout: float = 15.0, opener=None):
        self.endpoint = endpoint.strip()
        self.api_key = api_key
        self.timeout = timeout
        self.opener = opener or urlopen

    def _url(self, query: str) -> str:
        parts = urlsplit(self.endpoint)
        params = parse_qsl(parts.query, keep_blank_values=True)
        params.append(("q", query))
        return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(params), parts.fragment))

    def search(self, query: str) -> list[SearchFinding]:
        headers = {"Accept": "application/json", "User-Agent": "GEVER-LeadHunter/1.0"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        request = Request(self._url(query), headers=headers)

        try:
            with self.opener(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise RuntimeError(f"public search failed: {exc}") from exc

        rows = payload.get("results", []) if isinstance(payload, dict) else []
        findings = []
        for row in rows:
            if not isinstance(row, dict) or not row.get("url"):
                continue
            findings.append(SearchFinding(
                url=str(row.get("url", "")),
                title=str(row.get("title", "") or ""),
                snippet=str(row.get("snippet", "") or ""),
                domain=str(row.get("domain", "") or ""),
                published_at=row.get("published_at"),
                public_contact_method=row.get("public_contact_method"),
                location=row.get("location"),
                name=row.get("name"),
                organization=row.get("organization"),
            ))
        return findings


@dataclass(frozen=True)
class GeversLeadProfile:
    business_name: str = "Gevers Painting"
    locations: tuple[str, ...] = (
        "Myrtle Beach, SC",
        "Horry County, SC",
        "North Myrtle Beach, SC",
        "Conway, SC",
        "Surfside Beach, SC",
        "Socastee, SC",
        "Carolina Forest, SC",
    )
    services: tuple[str, ...] = (
        "interior painting",
        "exterior painting",
        "cabinet painting",
        "cabinet refinishing",
        "drywall repair painting",
        "commercial painting",
    )

    def queries(self) -> list[str]:
        primary_locations = ("Myrtle Beach", "Horry County")
        intent_terms = ("need painter", "painting quote", "painting estimate", "looking for painter")
        queries: list[str] = []
        for location in primary_locations:
            for service in self.services:
                queries.append(f'"{service}" "{location}"')
            for intent in intent_terms:
                queries.append(f'"{intent}" "{location}"')
        return queries
