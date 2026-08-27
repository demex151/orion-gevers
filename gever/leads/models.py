from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

class LeadClassification(str, Enum):
    HOT="HOT"; WARM="WARM"; PROSPECT="PROSPECT"
class LeadStatus(str, Enum):
    NEW="NEW"; REVIEWED="REVIEWED"; APPROVED="APPROVED"; CONTACTED="CONTACTED"; FOLLOW_UP="FOLLOW_UP"; WON="WON"; LOST="LOST"
class OpportunityType(str, Enum):
    ACTIVE_DEMAND="ACTIVE_DEMAND"; PROSPECT="PROSPECT"

@dataclass
class LeadCandidate:
    classification: LeadClassification; urgent: bool; score: float; opportunity_type: OpportunityType
    source_url: str; source_domain: str; evidence: str; dedupe_key: str
    name: Optional[str]=None; organization: Optional[str]=None; location: Optional[str]=None
    service_requested_or_inferred: Optional[str]=None; source_title: Optional[str]=None; published_at: Optional[str]=None
    public_contact_method: Optional[str]=None; missing_information: list[str]=field(default_factory=list)
    recommended_action: Optional[str]=None; validation_notes: Optional[str]=None

@dataclass
class LeadRecord(LeadCandidate):
    lead_id: str=""; status: LeadStatus=LeadStatus.NEW; discovered_at: Optional[str]=None
    first_seen_at: Optional[str]=None; last_seen_at: Optional[str]=None; evidence_history: list[dict]=field(default_factory=list)

@dataclass
class SearchRunSummary:
    run_id: str; trigger: str; started_at: str; ended_at: Optional[str]=None; raw_findings: int=0; accepted_leads: int=0
    rejected_findings: int=0; duplicate_merges: int=0; hot_count: int=0; warm_count: int=0; prospect_count: int=0
    errors: dict[str,str]=field(default_factory=dict)
