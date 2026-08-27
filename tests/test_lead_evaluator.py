from gever.leads import LeadClassification, OpportunityType
from gever.leads.evaluator import LeadEvaluator
from gever.leads.search import GeversLeadProfile, SearchFinding


def evaluator():
    return LeadEvaluator(GeversLeadProfile())


def test_rejects_finding_outside_service_area():
    result = evaluator().evaluate(SearchFinding(
        url="https://example.com/charleston-painter",
        title="Need a painter in Charleston",
        snippet="Looking for an interior painter in Charleston SC.",
    ))
    assert result.candidate is None
    assert result.rejection_reason == "outside_service_area"


def test_rejects_non_painting_finding():
    result = evaluator().evaluate(SearchFinding(
        url="https://example.com/myrtle-roof",
        title="Need roofer in Myrtle Beach",
        snippet="Looking for a roofing estimate in Myrtle Beach.",
    ))
    assert result.candidate is None
    assert result.rejection_reason == "unsupported_service"


def test_explicit_local_urgent_demand_becomes_hot_active_demand():
    finding = SearchFinding(
        url="https://example.com/posts/123",
        title="Need painter ASAP in Myrtle Beach",
        snippet="Looking for an interior painter. Need a painting quote today for my house in Myrtle Beach.",
        public_contact_method="public reply",
    )
    lead = evaluator().evaluate(finding).candidate
    assert lead is not None
    assert lead.opportunity_type is OpportunityType.ACTIVE_DEMAND
    assert lead.classification is LeadClassification.HOT
    assert lead.urgent is True
    assert lead.score >= 75


def test_local_painting_prospect_without_request_is_not_hot():
    finding = SearchFinding(
        url="https://example.com/property/55",
        title="Myrtle Beach property renovation",
        snippet="Commercial property in Myrtle Beach with exterior painting and drywall renovation planned.",
    )
    lead = evaluator().evaluate(finding).candidate
    assert lead is not None
    assert lead.opportunity_type is OpportunityType.PROSPECT
    assert lead.classification is not LeadClassification.HOT


def test_rejects_competing_painting_company_marketing_page():
    result = evaluator().evaluate(SearchFinding(
        url="https://paintingcompany.example/myrtle-beach",
        title="Professional painters in Myrtle Beach",
        snippet="Our painting contractors serve homeowners. Get a free painting estimate today!",
    ))
    assert result.candidate is None
    assert result.rejection_reason == "provider_marketing"


def test_rejects_directory_or_top_contractors_page():
    result = evaluator().evaluate(SearchFinding(
        url="https://directory.example/top-painters",
        title="Top 5 Painting Contractors in Myrtle Beach SC",
        snippet="Compare local painting contractors, reviews, ratings and estimates in Horry County.",
    ))
    assert result.candidate is None
    assert result.rejection_reason == "directory_or_listicle"


def test_rejects_painter_job_listing():
    result = evaluator().evaluate(SearchFinding(
        url="https://jobs.example/painter-jobs",
        title="Need Painter - Professional & Experienced",
        snippet="Painter job in Myrtle Beach. $18-$20 per hour according to experience.",
    ))
    assert result.candidate is None
    assert result.rejection_reason == "employment_listing"


def test_dedupe_key_is_deterministic_for_same_finding():
    first = SearchFinding(
        url="https://EXAMPLE.com/post/7/",
        title="Painter needed Myrtle Beach",
        snippet="Need exterior painting estimate in Myrtle Beach",
    )
    second = SearchFinding(
        url="https://example.com/post/7",
        title="Painter needed Myrtle Beach",
        snippet="Need exterior painting estimate in Myrtle Beach",
    )
    first_lead = evaluator().evaluate(first).candidate
    second_lead = evaluator().evaluate(second).candidate
    assert first_lead is not None and second_lead is not None
    assert first_lead.dedupe_key == second_lead.dedupe_key
