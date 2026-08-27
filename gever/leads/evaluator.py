import hashlib
import re
import unicodedata
from dataclasses import dataclass
from datetime import date, datetime
from urllib.parse import urlsplit, urlunsplit

from .models import LeadCandidate, LeadClassification, OpportunityType
from .search import GeversLeadProfile, SearchFinding


@dataclass(frozen=True)
class EvaluationResult:
    candidate: LeadCandidate | None = None
    rejection_reason: str | None = None


class LeadEvaluator:
    MAX_LEAD_AGE_DAYS = 30

    DEMAND_SIGNALS = (
        "need painter", "need a painter", "looking for painter", "looking for a painter",
        "recommend painter", "recommend a painter", "recommend a reliable painter",
        "recommendation for a painter", "painter recommendation", "painter recommendations",
        "painting quote", "painting estimate", "quote for painting", "estimate for painting",
        "hire painter", "hire a painter", "painter needed",
    )
    URGENCY_SIGNALS = ("asap", "urgent", "today", "this week", "immediately", "right away")
    CONTACT_SIGNALS = ("call", "text", "email", "message", "reply", "contact")

    EMPLOYMENT_SIGNALS = (
        "painter job", "painter jobs", "painting job opening", "job opening",
        "per hour", "hourly pay", "salary", "hiring painter", "now hiring",
        "employment", "apply now", "according to experience",
    )
    DIRECTORY_SIGNALS = (
        "top 5 painting", "top 10 painting", "best painting contractors",
        "compare local painting contractors", "compare expert painting contractors",
        "ratings and reviews", "customer reviews", "read reviews",
        "bbb directory", "directory of", "your guide to trusted", "superpages.com",
        "yellow pages", "find contact information",
    )
    PROVIDER_MARKETING_SIGNALS = (
        "our painting contractors", "our painters", "our painting professionals",
        "professional painting contractors", "reliable, professional painting contractors",
        "we specialize in", "we proudly serve", "serves homeowners", "serving homeowners",
        "get a free painting estimate", "get a free estimate today", "get a free estimate",
        "request your free quote", "request your free interior", "request your free exterior",
        "free painting estimate", "free estimate on residential", "free estimate on commercial",
        "schedule an appointment for your free", "book your free", "set up a free painting estimate",
        "call us today", "call us at", "call today", "contact us today", "our team", "our clientele",
    )
    RHETORICAL_PROVIDER_MARKETING_SIGNALS = (
        "need painters in", "need a painter for your", "need painters for your",
        "do you have old paint", "spruce up the appearance of your house",
        "spruce up the appearance of your office", "your house or office building",
    )
    PROVIDER_SELF_PROMOTION_SIGNALS = (
        "i own ", "my painting company", "my painting business", "our painting company",
        "i'm licensed and insured", "i am licensed and insured", "looking for new work",
        "looking for work", "available for painting work", "we are licensed and insured",
    )
    EXISTING_PROVIDER_RECOMMENDATION_SIGNALS = (
        "i highly recommend giving", "i recommend giving", "highly recommend giving",
        "contact john", "does amazing work", "they do amazing work",
    )

    MONTHS = {
        "jan": 1, "january": 1,
        "feb": 2, "february": 2,
        "mar": 3, "march": 3,
        "apr": 4, "april": 4,
        "may": 5,
        "jun": 6, "june": 6,
        "jul": 7, "july": 7,
        "aug": 8, "august": 8,
        "sep": 9, "sept": 9, "september": 9,
        "oct": 10, "october": 10,
        "nov": 11, "november": 11,
        "dec": 12, "december": 12,
    }

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

    def _location_aliases(self):
        aliases = set()
        for location in self.profile.locations:
            normalized = self._normalize(location)
            if normalized:
                aliases.add(normalized)
                city_or_county = normalized.split(",", 1)[0].strip()
                if city_or_county:
                    aliases.add(city_or_county)
        return aliases

    def _in_service_area(self, text: str) -> bool:
        return any(alias in text for alias in self._location_aliases())

    def _painting_related(self, text: str) -> bool:
        terms = set(self._normalize(service) for service in self.profile.services)
        terms.update(("paint", "painting", "painter", "drywall"))
        return any(term in text for term in terms)

    @staticmethod
    def _has_any(text: str, signals) -> bool:
        return any(signal in text for signal in signals)

    def _rejection_reason_for_non_customer(self, text: str) -> str | None:
        if self._has_any(text, self.EMPLOYMENT_SIGNALS):
            return "employment_listing"
        if self._has_any(text, self.DIRECTORY_SIGNALS):
            return "directory_or_listicle"
        if self._has_any(text, self.PROVIDER_MARKETING_SIGNALS):
            return "provider_marketing"
        if self._has_any(text, self.RHETORICAL_PROVIDER_MARKETING_SIGNALS):
            return "provider_marketing"
        if self._has_any(text, self.PROVIDER_SELF_PROMOTION_SIGNALS):
            return "provider_self_promotion"
        if self._has_any(text, self.EXISTING_PROVIDER_RECOMMENDATION_SIGNALS):
            return "no_buyer_intent"
        return None

    def _active_demand(self, text: str) -> bool:
        return self._has_any(text, self.DEMAND_SIGNALS)

    def _urgent(self, text: str) -> bool:
        return self._has_any(text, self.URGENCY_SIGNALS)

    def _dedupe_key(self, finding: SearchFinding) -> str:
        canonical = self._canonical_url(finding.url)
        identity = self._normalize(finding.name or finding.organization or finding.title)
        raw = f"{canonical}|{identity}".encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    def _lead_age_days(self, finding: SearchFinding) -> int | None:
        raw = " ".join(filter(None, (finding.published_at, finding.title, finding.snippet)))
        text = self._normalize(raw)

        if any(token in text for token in ("today", "just now", "minutes ago", "hours ago")):
            return 0
        if "yesterday" in text:
            return 1

        relative = re.search(r"\b(\d{1,3})\s+days?\s+ago\b", text)
        if relative:
            return int(relative.group(1))

        iso = re.search(r"\b(20\d{2})-(\d{1,2})-(\d{1,2})\b", text)
        if iso:
            try:
                published = date(int(iso.group(1)), int(iso.group(2)), int(iso.group(3)))
                return max(0, (date.today() - published).days)
            except ValueError:
                pass

        absolute = re.search(
            r"\b(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+(\d{1,2}),\s*(20\d{2})\b",
            text,
        )
        if absolute:
            month = self.MONTHS.get(absolute.group(1))
            if month:
                try:
                    published = date(int(absolute.group(3)), month, int(absolute.group(2)))
                    return max(0, (date.today() - published).days)
                except ValueError:
                    pass

        if finding.published_at:
            try:
                published = datetime.fromisoformat(finding.published_at.replace("Z", "+00:00")).date()
                return max(0, (date.today() - published).days)
            except ValueError:
                pass

        return None

    def evaluate(self, finding: SearchFinding) -> EvaluationResult:
        if not finding.url or not (finding.title or finding.snippet):
            return EvaluationResult(rejection_reason="insufficient_evidence")

        text = self._text(finding)
        if not self._in_service_area(text):
            return EvaluationResult(rejection_reason="outside_service_area")
        if not self._painting_related(text):
            return EvaluationResult(rejection_reason="unsupported_service")

        non_customer_reason = self._rejection_reason_for_non_customer(text)
        if non_customer_reason:
            return EvaluationResult(rejection_reason=non_customer_reason)

        active_demand = self._active_demand(text)
        if not active_demand:
            return EvaluationResult(rejection_reason="no_buyer_intent")

        age_days = self._lead_age_days(finding)
        if age_days is not None and age_days > self.MAX_LEAD_AGE_DAYS:
            return EvaluationResult(rejection_reason="stale_lead")

        urgent = self._urgent(text)
        score = 75.0
        if urgent:
            score += 15.0
        if finding.public_contact_method or self._has_any(text, self.CONTACT_SIGNALS):
            score += 10.0
        score = min(100.0, score)

        missing = []
        if not finding.name:
            missing.append("name")
        if not finding.public_contact_method:
            missing.append("public_contact_method")

        evidence = finding.snippet or finding.title
        return EvaluationResult(candidate=LeadCandidate(
            classification=LeadClassification.HOT,
            urgent=urgent,
            score=score,
            opportunity_type=OpportunityType.ACTIVE_DEMAND,
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
            recommended_action="Review evidence and contact manually",
            validation_notes="Local Gevers Painting V2 buyer-intent + freshness evaluation",
        ))
