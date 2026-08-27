# Gevers Lead Hunter V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a manual, testable Lead Hunter that discovers public painting opportunities for Gevers Painting in Myrtle Beach/Horry County, evaluates them, and persists prioritized leads for review.

**Architecture:** Keep Internet discovery behind a provider interface, keep deterministic business rules in a separate evaluator, and use the existing LeadStore as the persistence boundary. A LeadHunter orchestrator owns search-run accounting and failure isolation.

**Tech Stack:** Python 3.13, dataclasses, stdlib HTTP/JSON utilities where possible, SQLite through existing LeadStore, pytest.

**Spec:** `docs/superpowers/specs/2026-08-26-gevers-lead-hunter-v1-design.md`

## Global Constraints

- V1 is exclusively for Gevers Painting in Myrtle Beach/Horry County.
- Only public search findings are consumed.
- V1 must never contact prospects automatically.
- Existing LeadStore and LeadCandidate contracts remain the persistence boundary.
- Scores are deterministic from 0 to 100.
- HOT requires explicit active demand and score >= 75; WARM >= 50; otherwise PROSPECT.
- Provider failures must not discard successful findings from other providers.
- Existing repository tests must continue to pass.

---

### Task 1: Search finding and Gevers profile contracts

**Files:**
- Create: `gever/leads/search.py`
- Test: `tests/test_lead_search.py`

**Interfaces:**
- Produces: `SearchFinding`, `GeversLeadProfile`, `SearchProvider.search(query: str) -> list[SearchFinding]`, `GeversLeadProfile.queries() -> list[str]`.

- [ ] **Step 1: Write failing tests** for normalized findings and queries containing Myrtle Beach/Horry County plus supported painting services.
- [ ] **Step 2: Run** `py -m pytest tests/test_lead_search.py -v` and confirm failure because contracts do not exist.
- [ ] **Step 3: Implement** focused dataclasses/protocol and fixed Gevers V1 profile with supported locations/services and generated queries.
- [ ] **Step 4: Run** `py -m pytest tests/test_lead_search.py -v` and confirm pass.
- [ ] **Step 5: Commit** `feat: add Gevers lead search contracts`.

### Task 2: Deterministic evaluator

**Files:**
- Create: `gever/leads/evaluator.py`
- Test: `tests/test_lead_evaluator.py`

**Interfaces:**
- Consumes: `SearchFinding`, `GeversLeadProfile`.
- Produces: `EvaluationResult(candidate: LeadCandidate | None, rejection_reason: str | None)` and `LeadEvaluator.evaluate(finding) -> EvaluationResult`.

- [ ] **Step 1: Write failing tests** proving out-of-area and non-painting findings reject, explicit local painting demand becomes ACTIVE_DEMAND, HOT requires >=75 and active demand, and dedupe keys are stable.
- [ ] **Step 2: Run** `py -m pytest tests/test_lead_evaluator.py -v` and confirm failure.
- [ ] **Step 3: Implement** normalization, geography/service keyword checks, demand/urgency signals, 0-100 scoring, classification, recommended action, missing-information list, and SHA-256 based deterministic dedupe key.
- [ ] **Step 4: Run** evaluator tests and confirm pass.
- [ ] **Step 5: Commit** `feat: evaluate Gevers painting opportunities`.

### Task 3: Lead Hunter orchestration

**Files:**
- Create: `gever/leads/hunter.py`
- Test: `tests/test_lead_hunter.py`

**Interfaces:**
- Consumes: `LeadStore`, `LeadEvaluator`, `GeversLeadProfile`, list of `SearchProvider`.
- Produces: `LeadHunter.run(trigger: str = "manual") -> SearchRunSummary`.

- [ ] **Step 1: Write failing tests** with fake providers proving accepted/rejected counters, HOT/WARM/PROSPECT counters, duplicate merges, provider-error isolation, and finished run timestamp.
- [ ] **Step 2: Run** `py -m pytest tests/test_lead_hunter.py -v` and confirm failure.
- [ ] **Step 3: Implement** orchestration that starts one run, executes each profile query against providers, evaluates findings, records rejections, detects pre-existing dedupe keys, upserts accepted leads, updates counters, records provider exceptions, and always finishes the run.
- [ ] **Step 4: Run** hunter tests and confirm pass.
- [ ] **Step 5: Commit** `feat: orchestrate Gevers lead hunts`.

### Task 4: Public web-search provider boundary

**Files:**
- Modify: `gever/leads/search.py`
- Test: `tests/test_lead_search.py`

**Interfaces:**
- Produces: `JsonSearchProvider(endpoint: str, api_key: str | None = None, timeout: float = 15.0)` implementing `search(query)` and translating provider JSON into `SearchFinding`.

- [ ] **Step 1: Write failing tests** using a fake injected HTTP opener: successful JSON normalization, malformed rows skipped, HTTP/provider errors raised with useful context.
- [ ] **Step 2: Run** search tests and confirm failure.
- [ ] **Step 3: Implement** provider with dependency-injected opener, URL encoding, timeout, optional bearer key, JSON parsing, and normalized title/snippet/url/domain/published/contact fields.
- [ ] **Step 4: Run** search tests and confirm pass.
- [ ] **Step 5: Commit** `feat: add public search provider adapter`.

### Task 5: Manual Lead Hunter command

**Files:**
- Create: `run_lead_hunter.py`
- Modify: `gever/leads/__init__.py`
- Test: `tests/test_lead_hunter_cli.py`

**Interfaces:**
- Consumes: environment configuration for search endpoint/key, `LeadHunter`.
- Produces: CLI exit code 0 on completed run and a compact summary of counts plus prioritized stored leads.

- [ ] **Step 1: Write failing tests** for missing endpoint configuration and successful fake hunt summary without making real network calls.
- [ ] **Step 2: Run** `py -m pytest tests/test_lead_hunter_cli.py -v` and confirm failure.
- [ ] **Step 3: Implement** CLI wiring. Require `GEVER_SEARCH_ENDPOINT`; optionally read `GEVER_SEARCH_API_KEY`; print run counts and lead classification/score/evidence/source URL. Never contact leads.
- [ ] **Step 4: Run** CLI tests and confirm pass.
- [ ] **Step 5: Commit** `feat: add manual Gevers lead hunter command`.

### Task 6: Regression verification

**Files:**
- No production changes unless a regression is discovered.

- [ ] **Step 1: Run** `py -m pytest -v`.
- [ ] **Step 2: Confirm** all pre-existing 40 tests and 9 subtests still pass plus all new Lead Hunter tests.
- [ ] **Step 3: Run** a no-network CLI configuration test and confirm missing configuration fails clearly without altering the lead database.
- [ ] **Step 4: Review** the diff for accidental auto-contact behavior, credentials, hard-coded secrets, or unrelated refactors.
- [ ] **Step 5: Commit** only if verification requires a targeted fix.
