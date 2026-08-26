# GEVER Lead Hunter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build GEVER's first production subsystem: a local-first Lead Hunter that discovers live public organic painting opportunities, validates and deduplicates them, ranks them as HOT/WARM/PROSPECT plus URGENT, stores evidence locally, exposes them through an API/dashboard, and runs manually or every 2 hours.

**Architecture:** Keep Lead Hunter independent from GEVER conversational memory and voice internals. A Python `gever.leads` package owns domain models, SQLite persistence, public-web research, validation/scoring/deduplication, orchestration, and scheduling; FastAPI exposes a thin boundary; the existing React shell gets a Lead Hunter view and explicit task trigger without changing the established microphone/TTS flow.

**Tech Stack:** Python 3, FastAPI, SQLite (`sqlite3`), standard-library HTTP/parsing where practical, existing NVIDIA-backed GEVER brain for bounded semantic analysis where needed, React frontend, existing project test runners.

**Spec:** `docs/superpowers/specs/2026-08-26-gever-lead-hunter-design.md`

## Global Constraints

- Use only public, organically available information.
- Do not purchase lead databases or paid prospect data.
- Do not contact, message, post, submit forms, or otherwise reach out to anyone without explicit user approval.
- Do not bypass logins, access controls, robots/anti-bot restrictions, or private APIs.
- Do not modify the established GEVER wake-word, session, barge-in, memory, or TTS behavior.
- Lead records must be stored separately from `GeversMemory` conversational records.
- First production storage is local on the PC; no cloud synchronization or phone access in this plan.
- Manual search and automatic non-overlapping search every 2 hours are both required.
- HOT means ready to act; URGENT is an independent time-sensitivity flag.
- Unknown data remains null/empty and must never be invented.

---

### Task 1: Lead Domain Model and Local SQLite Store

**Files:**
- Create: `gever/leads/__init__.py`
- Create: `gever/leads/models.py`
- Create: `gever/leads/store.py`
- Create: `tests/test_lead_store.py`

**Interfaces:**
- Produces `LeadCandidate`, `LeadRecord`, `SearchRunSummary` dataclasses/enums.
- Produces `LeadStore(db_path=None)` with `upsert_lead(candidate)`, `list_leads()`, `get_lead(lead_id)`, `update_status(lead_id, status)`, `record_rejection(...)`, `start_run(trigger)`, and `finish_run(...)`.
- Default DB path: `<project>/data/leads.db`.

- [ ] **Step 1: Write failing persistence tests**

Create tests that instantiate `LeadStore` with a temporary SQLite path, insert a candidate, reload the store, and assert the same persistent `lead_id`, classification, urgency, evidence, source URL, timestamps, and workflow status are returned. Add a status transition test for `NEW -> APPROVED`.

- [ ] **Step 2: Run the focused test**

Run: `python -m pytest tests/test_lead_store.py -v`

Expected: FAIL because `gever.leads` does not exist.

- [ ] **Step 3: Implement domain types and schema**

Define exact enums:

```python
class LeadClassification(str, Enum):
    HOT = "HOT"
    WARM = "WARM"
    PROSPECT = "PROSPECT"

class LeadStatus(str, Enum):
    NEW = "NEW"
    REVIEWED = "REVIEWED"
    APPROVED = "APPROVED"
    CONTACTED = "CONTACTED"
    FOLLOW_UP = "FOLLOW_UP"
    WON = "WON"
    LOST = "LOST"

class OpportunityType(str, Enum):
    ACTIVE_DEMAND = "ACTIVE_DEMAND"
    PROSPECT = "PROSPECT"
```

Implement SQLite tables for `leads`, `lead_evidence`, `search_runs`, `rejected_findings`, and `lead_status_history`. Enable WAL mode and foreign keys. Generate persistent lead IDs with UUID4.

- [ ] **Step 4: Implement store operations**

`upsert_lead` must create a new lead or update `last_seen_at`/evidence on an existing dedupe key. `update_status` must write status history. `list_leads` must order urgent HOT first, then HOT, WARM, PROSPECT, and score descending within groups.

- [ ] **Step 5: Run persistence tests**

Run: `python -m pytest tests/test_lead_store.py -v`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add gever/leads tests/test_lead_store.py
git commit -m "feat: add local Lead Hunter storage"
```

### Task 2: Validation, Scoring, and Deduplication

**Files:**
- Create: `gever/leads/config.py`
- Create: `gever/leads/validator.py`
- Create: `gever/leads/scorer.py`
- Create: `gever/leads/dedupe.py`
- Create: `tests/test_lead_pipeline.py`

**Interfaces:**
- Produces `LeadTerritory` containing Myrtle Beach, North Myrtle Beach, Conway, Carolina Forest, Socastee, Surfside Beach, Garden City, Murrells Inlet, Little River, plus configurable nearby aliases.
- Produces `validate_candidate(candidate) -> ValidationResult`.
- Produces `score_candidate(candidate, validation) -> ScoredLead`.
- Produces `dedupe_key(candidate) -> str`.

- [ ] **Step 1: Write failing pipeline tests**

Test these concrete cases: `Need a painter this week in Conway` is service/location relevant and urgent; `Painter hiring experienced crew in Myrtle Beach` is rejected as employment/contractor noise; an old generic painting-directory page is rejected for insufficient opportunity evidence; a property manager with public maintenance/repainting evidence is accepted as PROSPECT; equivalent URLs/text normalize to the same dedupe key.

- [ ] **Step 2: Run tests to verify failure**

Run: `python -m pytest tests/test_lead_pipeline.py -v`

Expected: FAIL because validation/scoring modules do not exist.

- [ ] **Step 3: Implement territory and deterministic validation**

Keep service terms and territory aliases in `config.py`. Validation must return explicit reasons such as `outside_service_area`, `employment_post`, `contractor_advertising`, `stale_or_undated_generic_content`, `unsupported_service`, or `insufficient_evidence`.

- [ ] **Step 4: Implement scoring/classification**

Use deterministic weighted inputs for explicit need, recency, geography, service fit, evidence quality, reply/contact path, urgency, and buyer confidence. Enforce category rules: HOT requires verifiable evidence plus enough public information to act; WARM is real intent with missing action data; PROSPECT requires evidence-backed inferred need. URGENT is stored independently.

- [ ] **Step 5: Implement normalized dedupe key**

Normalize canonical URL, organization/name, location, contact clue, and evidence fingerprint. Never merge solely because two leads are in the same city.

- [ ] **Step 6: Run pipeline tests**

Run: `python -m pytest tests/test_lead_pipeline.py -v`

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add gever/leads/config.py gever/leads/validator.py gever/leads/scorer.py gever/leads/dedupe.py tests/test_lead_pipeline.py
git commit -m "feat: classify and deduplicate painting opportunities"
```

### Task 3: Public Web Research Engine

**Files:**
- Create: `gever/leads/research.py`
- Create: `gever/leads/strategies.py`
- Create: `tests/test_lead_research.py`

**Interfaces:**
- Produces `SearchStrategy(name, opportunity_type, query)`.
- Produces `build_search_strategies(territory) -> list[SearchStrategy]` for active demand and prospecting.
- Produces `PublicWebResearchEngine.search(strategy) -> list[LeadCandidate]`.
- Every candidate preserves source URL/domain/title/evidence/discovery time and publication time when exposed by the source.

- [ ] **Step 1: Write failing query-strategy tests**

Assert strategies include multiple active-demand phrasings for painter/house painting/interior/exterior/cabinets/drywall/pressure washing and multiple prospect strategies for property managers, Realtors, HOAs, rentals, renovations, and business maintenance across configured territory.

- [ ] **Step 2: Write failing parser tests with saved public-result fixtures**

Use small HTML/JSON fixtures representing public search results. Assert URLs, titles, snippets, dates when present, and source domains are extracted without inventing missing contact information.

- [ ] **Step 3: Run research tests**

Run: `python -m pytest tests/test_lead_research.py -v`

Expected: FAIL because research modules do not exist.

- [ ] **Step 4: Implement search strategy generation**

Generate bounded, location-specific queries rather than one broad query. Each strategy carries its opportunity type so downstream scoring knows whether intent is explicit or inferred.

- [ ] **Step 5: Implement public search adapter boundary**

Create an adapter interface that can execute ordinary public web searches through a configured search endpoint/provider available to the running GEVER installation. Credentials, if a provider requires them, must come from environment/config and never be committed. The adapter must respect HTTP failures/rate limits and must not attempt login bypasses or anti-bot evasion.

- [ ] **Step 6: Implement result normalization**

Convert public search results into `LeadCandidate` objects. Preserve evidence verbatim only as short snippets; fetch/open a public result page only when accessible normally and needed to validate the opportunity. Mark inaccessible pages as unavailable rather than bypassing controls.

- [ ] **Step 7: Run research tests**

Run: `python -m pytest tests/test_lead_research.py -v`

Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add gever/leads/research.py gever/leads/strategies.py tests/test_lead_research.py
git commit -m "feat: add public web research for Lead Hunter"
```

### Task 4: Lead Hunter Orchestrator and Run Diagnostics

**Files:**
- Create: `gever/leads/service.py`
- Create: `tests/test_lead_service.py`

**Interfaces:**
- Produces `LeadHunterService(store, research_engine)`.
- Produces `run(trigger: str) -> SearchRunSummary`.
- One run executes both active-demand and prospect strategies, validates each finding, deduplicates, stores accepted leads, records rejected findings, and returns counts/errors.

- [ ] **Step 1: Write failing orchestration tests**

Use a fake research engine returning accepted, rejected, duplicate, and source-error findings. Assert the run continues after one source error and records raw count, accepted count, rejected count, duplicate merges, classification counts, and per-source errors.

- [ ] **Step 2: Run service tests**

Run: `python -m pytest tests/test_lead_service.py -v`

Expected: FAIL because `LeadHunterService` does not exist.

- [ ] **Step 3: Implement orchestration**

For each strategy: search, normalize, validate, score, calculate dedupe key, persist or merge. Catch errors at strategy/source boundary so one failed source does not abort the whole run. Start and finish a `search_runs` record around every invocation.

- [ ] **Step 4: Run service tests**

Run: `python -m pytest tests/test_lead_service.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add gever/leads/service.py tests/test_lead_service.py
git commit -m "feat: orchestrate Lead Hunter production runs"
```

### Task 5: FastAPI Production Boundary

**Files:**
- Create: `backend/lead_routes.py`
- Modify: `backend/server.py`
- Create: `tests/test_lead_api.py`

**Interfaces:**
- `POST /api/leads/search` starts one manual search and returns its summary.
- `GET /api/leads` returns prioritized stored leads.
- `GET /api/leads/{lead_id}` returns one lead with evidence history.
- `PATCH /api/leads/{lead_id}/status` accepts one valid `LeadStatus`.
- `GET /api/leads/runs` returns recent run diagnostics.

- [ ] **Step 1: Write failing API tests**

Use FastAPI test client with a temporary LeadStore/service dependency. Assert list ordering, manual run response, valid status update, invalid status rejection, missing lead 404, and no outreach endpoint exists.

- [ ] **Step 2: Run API tests**

Run: `python -m pytest tests/test_lead_api.py -v`

Expected: FAIL because lead routes are not registered.

- [ ] **Step 3: Implement an isolated router**

Create `APIRouter(prefix="/api/leads")` in `backend/lead_routes.py`. Keep Lead Hunter construction in that module or a dedicated dependency function. `backend/server.py` should only import/include the router; do not insert research logic into voice endpoints.

- [ ] **Step 4: Run API and existing backend tests**

Run: `python -m pytest tests/test_lead_api.py -v`

Then run the existing backend/session/voice test suite.

Expected: PASS with existing voice behavior unchanged.

- [ ] **Step 5: Commit**

```bash
git add backend/lead_routes.py backend/server.py tests/test_lead_api.py
git commit -m "feat: expose Lead Hunter API"
```

### Task 6: Lead Hunter Dashboard

**Files:**
- Create: `frontend/src/LeadHunter.jsx`
- Create: `frontend/src/LeadHunter.css`
- Create: `frontend/src/leadClient.js`
- Create: `frontend/src/leadClient.test.js`
- Modify: `frontend/src/HomeShell.jsx`

**Interfaces:**
- `leadClient.list()`, `leadClient.searchNow()`, `leadClient.updateStatus(leadId, status)`, `leadClient.getRuns()`.
- `LeadHunter` renders prioritized lead cards/table and workflow controls.
- Existing voice conversation loop remains unchanged.

- [ ] **Step 1: Write failing client tests**

Assert exact HTTP methods/paths for list, manual search, and status update; assert API errors surface useful messages.

- [ ] **Step 2: Run client tests**

Run: `cd frontend && npm test -- --run src/leadClient.test.js`

Expected: FAIL because `leadClient.js` does not exist.

- [ ] **Step 3: Implement API client**

Use the existing backend base URL convention. Do not add a second microphone/session controller.

- [ ] **Step 4: Build dashboard UI**

Render HOT+URGENT first with a strong visual priority treatment, then HOT, WARM, PROSPECT. Each lead displays service, location, source/evidence, discovered/published time, public reply/contact path, missing information, recommended action, score, and workflow status. Provide buttons/selectors for APPROVED, CONTACTED, FOLLOW_UP, and LOST.

- [ ] **Step 5: Integrate a Lead Hunter navigation entry**

Add a `Lead Hunter` section to the existing shell navigation/agent surface. Opening it changes only the main content area and must not change session state or voice ownership.

- [ ] **Step 6: Run frontend tests**

Run: `cd frontend && npm test -- --run`

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add frontend/src/LeadHunter.jsx frontend/src/LeadHunter.css frontend/src/leadClient.js frontend/src/leadClient.test.js frontend/src/HomeShell.jsx
git commit -m "feat: add GEVER Lead Hunter dashboard"
```

### Task 7: Non-Overlapping Two-Hour Scheduler

**Files:**
- Create: `gever/leads/scheduler.py`
- Create: `tests/test_lead_scheduler.py`
- Modify: `backend/lead_routes.py`
- Modify: `backend/server.py`

**Interfaces:**
- Produces `LeadHunterScheduler(service, interval_seconds=7200)` with `start()`, `stop()`, and `run_if_idle(trigger="scheduled")`.
- Only one Lead Hunter run may execute at a time.

- [ ] **Step 1: Write failing scheduler tests**

Use a fake slow service and assert a second scheduled invocation while the first is active is skipped, not overlapped. Assert `stop()` terminates the scheduler cleanly.

- [ ] **Step 2: Run scheduler tests**

Run: `python -m pytest tests/test_lead_scheduler.py -v`

Expected: FAIL because scheduler does not exist.

- [ ] **Step 3: Implement scheduler with lock/event**

Use `threading.Lock`/`Event` and a daemon worker. Default interval is exactly `7200` seconds. Manual API runs and scheduled runs must share the same service run lock so they cannot overlap.

- [ ] **Step 4: Attach lifecycle without touching audio lifecycle semantics**

Start Lead Hunter scheduler during FastAPI startup after existing services initialize; stop it during shutdown. Failures starting Lead Hunter must be logged and must not prevent GEVER voice/chat startup.

- [ ] **Step 5: Run scheduler and backend regression tests**

Run: `python -m pytest tests/test_lead_scheduler.py tests/test_lead_api.py -v`

Then run the existing backend suite.

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add gever/leads/scheduler.py backend/lead_routes.py backend/server.py tests/test_lead_scheduler.py
git commit -m "feat: schedule Lead Hunter every two hours"
```

### Task 8: Explicit GEVER Command Routing

**Files:**
- Create: `gever/task_router.py`
- Create: `tests/test_task_router.py`
- Modify: `backend/server.py`

**Interfaces:**
- Produces `route_task_command(message) -> TaskIntent | None`.
- Recognizes explicit Spanish Lead Hunter commands such as `busca nuevos clientes`, `busca oportunidades de pintura`, and `ejecuta lead hunter`.
- Chat endpoint invokes Lead Hunter only for a recognized explicit task; all other messages continue through `GeversBrain.think()` unchanged.

- [ ] **Step 1: Write failing routing tests**

Assert explicit search commands map to `LEAD_HUNTER_SEARCH`. Assert ordinary conversation such as `¿cómo consigo más clientes?` remains normal chat and does not launch production work.

- [ ] **Step 2: Run routing tests**

Run: `python -m pytest tests/test_task_router.py -v`

Expected: FAIL because task router does not exist.

- [ ] **Step 3: Implement conservative command routing**

Use deterministic phrase/intent rules for the first version. Do not let an LLM casually infer production execution from ambiguous conversation. Return a short Spanish summary such as `Lead Hunter terminó: 3 nuevas oportunidades, 1 HOT, 1 WARM, 1 PROSPECT.` after a completed manual run.

- [ ] **Step 4: Wire only the chat task boundary**

At the start of `/api/chat`, check for an explicit production intent. If absent, execute the current `brain.think(message)` path exactly as before. If present, invoke Lead Hunter service and return the run summary as the answer so the existing TTS path can speak it.

- [ ] **Step 5: Run task-router and chat regressions**

Run: `python -m pytest tests/test_task_router.py tests/test_lead_api.py -v`

Then run existing chat/session tests.

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add gever/task_router.py backend/server.py tests/test_task_router.py
git commit -m "feat: route explicit GEVER lead search commands"
```

### Task 9: Live Field Verification and Production Guardrails

**Files:**
- Modify only if a verified defect requires a scoped fix.

**Interfaces:**
- Verifies the complete spec end-to-end with real public Internet search on the user's PC.

- [ ] **Step 1: Run complete automated tests**

Run the complete Python test suite and complete frontend test suite.

Expected: PASS before field testing.

- [ ] **Step 2: Start GEVER normally**

Start the existing backend and frontend using the same commands already used for the stable voice system. Confirm ORION activation, conversation, single TTS playback, and barge-in still work before running Lead Hunter.

- [ ] **Step 3: Trigger a real manual search from the dashboard**

Expected: a search run completes or reports source-specific public-web errors without breaking GEVER. Inspect accepted leads and rejected diagnostics.

- [ ] **Step 4: Trigger by voice/chat**

Say `GEVER, busca nuevos clientes.` Expected: the same Lead Hunter service runs once, the dashboard receives stored results, and GEVER returns a concise run summary.

- [ ] **Step 5: Verify evidence and no fabrication**

Open several accepted leads. Confirm every material claim is traceable to stored public evidence/source. Missing phone/email/contact information must remain missing rather than generated.

- [ ] **Step 6: Verify no outreach capability exists**

Confirm there is no endpoint/button/task that sends email, DMs, comments, forms, calls, or social posts.

- [ ] **Step 7: Verify scheduler behavior**

Using a test-configured short interval locally, confirm repeated scheduler ticks do not overlap. Restore production interval to exactly 7200 seconds before finalizing.

- [ ] **Step 8: Commit only verified scoped fixes**

Do not create an empty verification commit.