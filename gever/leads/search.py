from dataclasses import dataclass
from typing import Protocol
from urllib.parse import urlparse

@dataclass
class SearchFinding:
    url: str; title: str=""; snippet: str=""; domain: str=""; published_at: str|None=None
    public_contact_method: str|None=None; location: str|None=None; name: str|None=None; organization: str|None=None
    def __post_init__(self):
        self.url=(self.url or "").strip(); self.title=(self.title or "").strip(); self.snippet=(self.snippet or "").strip()
        self.domain=(self.domain or "").strip().lower() or ((urlparse(self.url).hostname or "").lower() if self.url else "")

class SearchProvider(Protocol):
    def search(self, query: str) -> list[SearchFinding]: ...

class DdgsSearchProvider:
    name="ddgs_local"
    def __init__(self, max_results=8, region="us-en", backend="auto", ddgs_factory=None):
        self.max_results=max_results; self.region=region; self.backend=backend; self._factory=ddgs_factory
    def search(self, query: str) -> list[SearchFinding]:
        try:
            if self._factory is None:
                from ddgs import DDGS
                engine=DDGS(timeout=10)
            else:
                engine=self._factory()
            rows=engine.text(query, region=self.region, safesearch="moderate", max_results=self.max_results, backend=self.backend)
        except Exception as exc:
            raise RuntimeError(f"DDGS search failed: {exc}") from exc
        findings=[]
        for row in rows or []:
            if not isinstance(row, dict): continue
            url=row.get("href") or row.get("url")
            if not url: continue
            findings.append(SearchFinding(url=str(url), title=str(row.get("title") or ""), snippet=str(row.get("body") or row.get("snippet") or "")))
        return findings

@dataclass(frozen=True)
class GeversLeadProfile:
    business_name: str="Gevers Painting"
    locations: tuple[str,...]=("Myrtle Beach, SC","Horry County, SC","North Myrtle Beach, SC","Conway, SC","Surfside Beach, SC","Socastee, SC","Carolina Forest, SC")
    services: tuple[str,...]=("interior painting","exterior painting","cabinet painting","cabinet refinishing","drywall repair painting","commercial painting")
    def queries(self):
        queries=[]
        for location in ("Myrtle Beach","Horry County"):
            for service in self.services: queries.append(f'"{service}" "{location}"')
            for intent in ("need painter","painting quote","painting estimate","looking for painter"): queries.append(f'"{intent}" "{location}"')
        return queries
