import hashlib
import re
import unicodedata
from dataclasses import dataclass
from urllib.parse import urlsplit, urlunsplit

from .models import LeadCandidate, LeadClassification, OpportunityType
from .search import GeversLeadProfile, SearchFinding


@dataclass(frozen=True)
class EvaluationResult:
    candidate: LeadCandidate | None = None
    rejection_reason: str | None = None


class LeadEvaluator:
    DEMAND_SIGNALS = (
        "need painter", "need a painter", "looking for painter", "looking for a painter",
        "recommend painter", "recommend a painter", "painter recommendation",
        "painting quote", "painting estimate", "quote for painting", "estimate for painting",
        "painting contractor", "hire painter", "hire a painter", "painter needed",
    )
    URGENCY_SIGNALS = ("asap", "urgent", "today", "this week", "immediately", "right away")
    CONTACT_SIGNALS = ("call", "text", "email", "message", "reply", "contact")

    def __init__(self, profile: GeversLeadProfile | None = None):
        self.profile = profile or GeversLeadProfile()

    @staticmethod
    def _normalize(value: str | None) -> str:
        value = unicodedata.normalize("NFKD", value or "")
        value = "".join(ch for ch in value if not unicodedata.combining(ch))
        return re.sub(r"\s+", " ", value.lower()).strip()

    @staticmethod
    def _canonical_url(url: str) -> str:
        parts = urlsplit(url.strip())
        path = parts.path.rstrip("/") or "/"
        return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, parts.query, ""))

    def _text(self, finding: SearchFinding) -> str:
        return self._normalize(" ".join(filter(None, (finding.title, finding.snippet, finding.location))))

    def _in_service_area(self, text: str) -> bool:
        return any(self._normalize(location) in text for location in self.profile.locations)

    def _painting_related(self, text: str) -> bool:
        terms = set(self._normalize(service) for service in self.profile.services)
        terms.update(("paint", "painting", "painter", "drywall"))
        return any(term in text for term in terms)

    def _active_demand(self, text: str) -> bool:
        return any(signal in text for signal in self.DEMAND_SIGNALS)

    def _urgent(self, text: str) -> bool:
        return any(signal in text for signal in self.URGENCY_SIGNALS)

    def _dedupe_key(self, finding: SearchFinding) -> str:
        canonical = self._canonical_url(finding.url)
        identity = self._normalize(finding.name or finding.organization or finding.title)
        raw = f"{canonical}|{identity}".encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    def evaluate(self, finding: SearchFinding) -> EvaluationResult:
        if not finding.url or not (finding.title or finding.snippet):
            return EvaluationResult(rejection_reason="insufficient_evidence")

        text = self._text(finding)
        if not self._in_service_area(text):
            return EvaluationResult(rejection_reason="outside_service_area")
        if not self._painting_related(text):
            return EvaluationResult(rejection_reason="unsupported_service")

        active_demand = self._active_demand(text)
        urgent = self._urgent(text)
        opportunity_type = OpportunityType.ACTIVE_DEMAND if active_demand else OpportunityType.PROSPECT

        score = 25.0  # verified local geography
        score += 25.0  # supported painting service
        if active_demand:
            score += 25.0
        if urgent:
            score += 15.0
        if finding.public_contact_method or any(signal in text for signal in self.CONTACT_SIGNALS):
            score += 10.0
        score = min(100.0, score)

        if active_demand and score >= 75:
            classification = LeadClassification.HOT
        elif score >= 50:
            classification = LeadClassification.WARM
        else:
            classification = LeadClassification.PROSPECT

        missing = []
        if not finding.name:
            missing.append("name")
        if not finding.public_contact_method:
            missing.append("public_contact_method")

        evidence = finding.snippet or finding.title
        return EvaluationResult(candidate=LeadCandidate(
            classification=classification,
            urgent=urgent,
            score=score,
            opportunity_type=opportunity_type,
            source_url=self._canonical_url(finding.url),
            source_domain=finding.domain,
            evidence=evidence,
            dedupe_key=self._dedupe_key(finding),
            name=finding.name,
            organization=finding.organization,
            location=finding.location,
            service_requested_or_inferred="painting",
            source_title=finding.title,
            published_at=finding.published_at,
            public_contact_method=finding.public_contact_method,
            missing_information=missing,
            recommended_action="Review evidence and contact manually" if active_demand else "Review as local painting prospect",
            validation_notes="Local Gevers Painting V1 deterministic evaluation",
        ))
