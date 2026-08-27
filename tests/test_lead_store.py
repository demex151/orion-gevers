from gever.leads import LeadCandidate, LeadClassification, LeadStatus, LeadStore, OpportunityType


def candidate(key="conway-painter"):
    return LeadCandidate(
        classification=LeadClassification.HOT,
        urgent=True,
        score=94.0,
        opportunity_type=OpportunityType.ACTIVE_DEMAND,
        source_url="https://example.com/post/1",
        source_domain="example.com",
        evidence="Need a painter this week in Conway",
        dedupe_key=key,
        name="Public Customer",
        location="Conway, SC",
        service_requested_or_inferred="Interior painting",
        public_contact_method="Reply on original public post",
        recommended_action="Review and approve reply",
    )


def test_lead_persists_with_same_id_and_evidence(tmp_path):
    db = tmp_path / "leads.db"
    first = LeadStore(db).upsert_lead(candidate())
    second = LeadStore(db).get_lead(first.lead_id)

    assert second.lead_id == first.lead_id
    assert second.classification == LeadClassification.HOT
    assert second.urgent is True
    assert second.status == LeadStatus.NEW
    assert second.source_url == "https://example.com/post/1"
    assert second.evidence_history[0]["evidence"] == "Need a painter this week in Conway"
    assert second.first_seen_at
    assert second.last_seen_at


def test_duplicate_candidate_keeps_persistent_lead_id(tmp_path):
    store = LeadStore(tmp_path / "leads.db")
    first = store.upsert_lead(candidate())
    second = store.upsert_lead(candidate())

    assert second.lead_id == first.lead_id
    assert len(store.list_leads()) == 1


def test_status_transition_is_persisted(tmp_path):
    db = tmp_path / "leads.db"
    store = LeadStore(db)
    lead = store.upsert_lead(candidate())

    updated = store.update_status(lead.lead_id, LeadStatus.APPROVED)
    reloaded = LeadStore(db).get_lead(lead.lead_id)

    assert updated.status == LeadStatus.APPROVED
    assert reloaded.status == LeadStatus.APPROVED


def test_list_prioritizes_hot_urgent(tmp_path):
    store = LeadStore(tmp_path / "leads.db")
    warm = candidate("warm")
    warm.classification = LeadClassification.WARM
    warm.urgent = False
    warm.score = 99
    hot = candidate("hot")
    hot.score = 80

    store.upsert_lead(warm)
    store.upsert_lead(hot)

    results = store.list_leads()
    assert results[0].dedupe_key == "hot"
