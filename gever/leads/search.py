from dataclasses import dataclass
from typing import Protocol
from urllib.parse import urlparse


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
