from gever.leads.telemetry import LeadHunterTelemetry


def test_results_display_request_increments_without_changing_hunt_state():
    telemetry = LeadHunterTelemetry()
    before = telemetry.snapshot()
    token = telemetry.request_results_display()
    after = telemetry.snapshot()

    assert token == 1
    assert after["display_request"] == 1
    assert after["state"] == before["state"] == "idle"


def test_results_display_requests_are_monotonic():
    telemetry = LeadHunterTelemetry()
    assert telemetry.request_results_display() == 1
    assert telemetry.request_results_display() == 2
    assert telemetry.snapshot()["display_request"] == 2
