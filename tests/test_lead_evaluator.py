from gever.leads import LeadClassification, OpportunityType
from gever.leads.evaluator import LeadEvaluator
from gever.leads.search import GeversLeadProfile, SearchFinding


def evaluator():
    return LeadEvaluator(GeversLeadProfile())


def test_rejects_finding_outside_service_area():
    result = evaluator().evaluate(SearchFinding(url="https://example.com/charleston-painter", title="Need a painter in Charleston", snippet="Looking for an interior painter in Charleston SC."))
    assert result.candidate is None
    assert result.rejection_reason == "outside_service_area"


def test_rejects_non_painting_finding():
    result = evaluator().evaluate(SearchFinding(url="https://example.com/myrtle-roof", title="Need roofer in Myrtle Beach", snippet="Looking for a roofing estimate in Myrtle Beach."))
    assert result.candidate is None
    assert result.rejection_reason == "unsupported_service"


def test_explicit_local_urgent_demand_becomes_hot_active_demand():
    finding = SearchFinding(url="https://example.com/posts/123", title="Need painter ASAP in Myrtle Beach", snippet="Looking for an interior painter. Need a painting quote today for my house in Myrtle Beach.", public_contact_method="public reply")
    lead = evaluator().evaluate(finding).candidate
    assert lead is not None
    assert lead.opportunity_type is OpportunityType.ACTIVE_DEMAND
    assert lead.classification is LeadClassification.HOT
    assert lead.urgent is True
    assert lead.score >= 75


def test_local_painting_content_without_buyer_intent_is_rejected():
    result = evaluator().evaluate(SearchFinding(url="https://example.com/property/55", title="Myrtle Beach property renovation", snippet="Commercial property in Myrtle Beach with exterior painting and drywall renovation planned."))
    assert result.candidate is None
    assert result.rejection_reason == "no_buyer_intent"


def test_rejects_competing_painting_company_marketing_page():
    result = evaluator().evaluate(SearchFinding(url="https://paintingcompany.example/myrtle-beach", title="Professional painters in Myrtle Beach", snippet="Our painting contractors serve homeowners. Get a free painting estimate today!"))
    assert result.candidate is None
    assert result.rejection_reason == "provider_marketing"


def test_rejects_directory_or_top_contractors_page():
    result = evaluator().evaluate(SearchFinding(url="https://directory.example/top-painters", title="Top 5 Painting Contractors in Myrtle Beach SC", snippet="Compare local painting contractors, reviews, ratings and estimates in Horry County."))
    assert result.candidate is None
    assert result.rejection_reason == "directory_or_listicle"


def test_rejects_painter_job_listing():
    result = evaluator().evaluate(SearchFinding(url="https://jobs.example/painter-jobs", title="Need Painter - Professional & Experienced", snippet="Painter job in Myrtle Beach. $18-$20 per hour according to experience."))
    assert result.candidate is None
    assert result.rejection_reason == "employment_listing"


def test_rejects_real_competitor_call_for_free_estimate():
    result = evaluator().evaluate(SearchFinding(url="https://mackpainters.com/myrtlebeach", title="Myrtle Beach Painters", snippet="Call us at (843) 353-6567 right now to schedule an appointment for your free painting estimate."))
    assert result.candidate is None


def test_rejects_real_competitor_request_your_free_estimate():
    result = evaluator().evaluate(SearchFinding(url="https://certapro.com/myrtle-beach/estimate", title="Free Painting Estimate", snippet="Request Your Free Interior or Exterior Home Painting Estimate Get a Free Estimate 843-839-1973 Myrtle Beach, SC 29577"))
    assert result.candidate is None


def test_rejects_real_competitor_service_marketing():
    result = evaluator().evaluate(SearchFinding(url="https://dunespainting.com/", title="Painting Myrtle Beach", snippet="Call us at 843-267-9341 for a free estimate on residential or commercial painting. Reliable, professional painting contractors covering the entire Myrtle Beach area."))
    assert result.candidate is None


def test_rejects_real_directory_yellow_pages():
    result = evaluator().evaluate(SearchFinding(url="https://www.yellowpages.com/myrtle-beach-sc/painting-contractors", title="Painting Contractors Myrtle Beach", snippet="Local Painting Contractors in Myrtle Beach, SC. Compare expert Painting Contractors, read reviews, and find contact information - THE REAL YELLOW PAGES"))
    assert result.candidate is None


def test_rejects_recommendation_of_existing_painter_as_not_new_demand():
    result = evaluator().evaluate(SearchFinding(url="https://www.facebook.com/groups/lorissouthcarolina/posts/2466238837107843", title="Loris South Carolina", snippet="Contact John Larrimore with E&J Custom Painting, very reasonable and professional. I highly recommend giving Coastal Myrtle Beach Handymen a call first. They do amazing work and offer free estimates."))
    assert result.candidate is None
    assert result.rejection_reason == "no_buyer_intent"


def test_rejects_contractor_looking_for_work():
    result = evaluator().evaluate(SearchFinding(url="https://www.facebook.com/groups/northmyrtlebeachsc/permalink/2342159202867125", title="Myrtle Beach contractor question", snippet="Where do homeowners in Myrtle Beach find a new contractor? I own Carolina Painting Pros LLC. I'm licensed and insured and looking for new work."))
    assert result.candidate is None
    assert result.rejection_reason == "provider_self_promotion"


def test_accepts_real_person_looking_for_painter():
    result = evaluator().evaluate(SearchFinding(url="https://www.facebook.com/groups/murrellsinlet/posts/2240309023077096", title="North Myrtle Beach", snippet="Looking for painter Gregg in North Myrtle Beach. Hello guys I am looking for a painter."))
    assert result.candidate is not None
    assert result.candidate.opportunity_type is OpportunityType.ACTIVE_DEMAND


def test_accepts_person_asking_for_painter_recommendations():
    result = evaluator().evaluate(SearchFinding(url="https://example.com/community/88", title="North Myrtle Beach recommendations", snippet="Can anyone recommend a reliable painter in North Myrtle Beach for my living room?"))
    assert result.candidate is not None
    assert result.candidate.opportunity_type is OpportunityType.ACTIVE_DEMAND


def test_rejects_stale_2024_buyer_request():
    result = evaluator().evaluate(SearchFinding(url="https://facebook.com/groups/old/post1", title="Horry County painter recommendations", snippet="Sep 3, 2024 · Any painter recommendations? Need interior doors sprayed in Horry County."))
    assert result.candidate is None
    assert result.rejection_reason == "stale_lead"


def test_rejects_stale_2023_buyer_request():
    result = evaluator().evaluate(SearchFinding(url="https://facebook.com/groups/old/post2", title="Horry County painter recommendations", snippet="Aug 16, 2023 · Licensed and insured painter recommendations needed in Horry County."))
    assert result.candidate is None
    assert result.rejection_reason == "stale_lead"


def test_rejects_stale_2025_buyer_request():
    result = evaluator().evaluate(SearchFinding(url="https://facebook.com/groups/old/post3", title="Myrtle Beach painter recommendations", snippet="Aug 7, 2025 · Licensed and insured painter recommendations needed in Myrtle Beach."))
    assert result.candidate is None
    assert result.rejection_reason == "stale_lead"


def test_accepts_relative_two_days_ago_request():
    result = evaluator().evaluate(SearchFinding(url="https://facebook.com/groups/recent/post1", title="Myrtle Beach painter recommendations", snippet="2 days ago · Shore Drive condo interior painter recommendations in Myrtle Beach."))
    assert result.candidate is not None


def test_accepts_relative_five_days_ago_request():
    result = evaluator().evaluate(SearchFinding(url="https://facebook.com/groups/recent/post2", title="Horry County painter recommendations", snippet="5 days ago · House painter recommendations for interior painting in Horry County."))
    assert result.candidate is not None


def test_dedupe_key_is_deterministic_for_same_finding():
    first = SearchFinding(url="https://EXAMPLE.com/post/7/", title="Painter needed Myrtle Beach", snippet="Need exterior painting estimate for my house in Myrtle Beach")
    second = SearchFinding(url="https://example.com/post/7", title="Painter needed Myrtle Beach", snippet="Need exterior painting estimate for my house in Myrtle Beach")
    first_lead = evaluator().evaluate(first).candidate
    second_lead = evaluator().evaluate(second).candidate
    assert first_lead is not None and second_lead is not None
    assert first_lead.dedupe_key == second_lead.dedupe_key
