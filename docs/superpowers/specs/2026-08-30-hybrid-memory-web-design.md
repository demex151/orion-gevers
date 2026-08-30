# GEVER Hybrid Memory and Web Learning Design

**Date:** 2026-08-30  
**Status:** Proposed for implementation  
**Base branch:** `feat/task-runtime`  
**Design branch:** `design/hybrid-memory-web`

## 1. Purpose

GEVER needs to respond faster, show its work in real time, retrieve prior knowledge efficiently, and learn useful facts from public web research without treating every page as truth. NVIDIA Nemotron remains the primary reasoning model, but simple local and memory operations must not call it unnecessarily.

This design adds four coordinated capabilities:

1. a fast request router;
2. a durable activity and knowledge memory;
3. a controlled web-research pipeline with sources;
4. a real-time activity feed for the frontend.

The implementation must preserve the current verified task runtime, voice system, Lead Hunter, existing memory contracts, and NVIDIA configuration.

## 2. Scope

### Included

- Local routing for deterministic status, task, and memory requests.
- Retrieval from local memory before external model calls.
- Web research through a provider interface.
- Source capture, deduplication, scoring, expiry, and provenance.
- Safe automatic storage of low-risk sourced facts.
- Required confirmation for sensitive or consequential memories.
- Append-only activity events for requests and task steps.
- Three-level retrieval: index, timeline, and full observations.
- Server-Sent Events (SSE) for live activity updates.
- REST fallback for reconnects and historical activity.
- Privacy redaction and an explicit no-store mode.
- Tests for routing, persistence, learning policy, events, API contracts, and failure modes.

### Excluded from the first version

- General browser automation, form submission, or authenticated websites.
- Autonomous posting to Facebook, Instagram, or Google Business.
- Team synchronization, cloud memory, enterprise administration, or multi-tenant RBAC.
- A vector database dependency.
- Replacing NVIDIA Nemotron.
- Automatically storing credentials, financial data, or arbitrary full web pages.
- Barge-in or other voice-flow changes.

## 3. Design Principles

- **Local first:** deterministic requests resolve locally.
- **Memory before web:** existing knowledge is checked before external research.
- **Evidence before storage:** web facts require provenance.
- **Small context:** NVIDIA receives selected evidence, not the entire memory.
- **Append-only observability:** every meaningful step produces an immutable activity event.
- **Safe failure:** GEVER reports unavailable sources or model failures and never fabricates completion.
- **Private by default:** secrets and explicitly private content are never persisted.
- **Provider independence:** customers can select their own supported model or search provider later.

## 4. Request Flow

1. FastAPI receives a text or transcribed voice request and assigns a `request_id`.
2. The activity recorder emits `request.received`.
3. The request router classifies the request as:
   - `local`
   - `memory`
   - `task`
   - `web`
   - `reasoning`
4. Deterministic local requests return without NVIDIA.
5. Memory requests search the compact index first and fetch details only for selected IDs.
6. Task requests are delegated to the existing `TaskRouter` and `TaskRuntime`.
7. Web requests call the search-provider interface, normalize evidence, deduplicate sources, and apply quality rules.
8. NVIDIA receives only the request, compact relevant memory, and selected source evidence.
9. The memory policy evaluates candidate facts.
10. Safe facts are stored with provenance; consequential candidates remain pending confirmation.
11. The activity recorder emits `request.completed` or `request.failed`.
12. The frontend receives each event over SSE and updates its activity panels.

## 5. Fast Request Router

### Route contract

```python
@dataclass(frozen=True)
class RouteDecision:
    route: Literal["local", "memory", "task", "web", "reasoning"]
    confidence: float
    reason: str
```

The router is deterministic in version one. It uses explicit patterns and existing task capabilities; it does not call NVIDIA merely to select a route.

### Local examples

- current system status;
- current task progress;
- open or close a known panel;
- end the conversation;
- list recently completed activities;
- read already-known business facts.

Ambiguous or generative requests use `reasoning`. Requests containing freshness cues such as “today,” “latest,” “currently,” or explicit search language use `web`.

## 6. Activity Memory

### Activity event

```python
@dataclass(frozen=True)
class ActivityEvent:
    id: str
    request_id: str
    sequence: int
    event_type: str
    status: Literal["started", "progress", "completed", "failed"]
    summary: str
    detail: dict[str, object]
    source_ids: tuple[str, ...]
    created_at: str
```

Events are append-only. Sequence numbers are monotonic within each request. Sensitive values are redacted before persistence.

Initial event types include:

- `request.received`
- `route.selected`
- `memory.search.started`
- `memory.search.completed`
- `web.search.started`
- `web.source.accepted`
- `web.source.rejected`
- `reasoning.started`
- `reasoning.completed`
- `memory.candidate.created`
- `memory.fact.saved`
- `memory.confirmation.required`
- `task.progress`
- `request.completed`
- `request.failed`

### Storage

SQLite remains the durable store. New tables are created through an idempotent schema initializer:

- `activity_events`
- `knowledge_sources`
- `knowledge_facts`
- `memory_candidates`

Writes use transactions, a busy timeout, and existing concurrency conventions. Event history is bounded through configurable retention; the first default is 30 days for detailed activity while durable facts remain until deleted or expired.

## 7. Knowledge and Provenance

### Source record

A source contains:

- stable ID;
- canonical URL;
- title;
- publisher/domain;
- retrieval timestamp;
- publication timestamp when available;
- selected excerpt or normalized summary;
- content hash;
- quality score.

Full pages are not stored by default.

### Knowledge fact

A fact contains:

- stable ID;
- normalized statement;
- category;
- business/project scope;
- confidence;
- source IDs;
- created and updated timestamps;
- expiry timestamp when applicable;
- review state;
- superseded fact ID when replaced.

A fact without a source may exist only when it comes directly from José or an explicit local business configuration. Web-derived facts require at least one source.

## 8. Controlled Web Learning

### Provider interface

```python
class WebSearchProvider(Protocol):
    def search(self, query: str, limit: int = 8) -> list[WebFinding]:
        ...
```

The existing DDGS-based search capability may implement this interface, but the memory subsystem cannot depend directly on DDGS. This keeps search replaceable and testable.

### Learning policy

The evaluator produces one of:

- `save`
- `pending_confirmation`
- `discard`

Automatic `save` is allowed only when all conditions hold:

- the content is a factual claim rather than an instruction or opinion;
- at least one attributable source exists;
- confidence meets the configured threshold;
- it is not sensitive;
- it does not authorize an external action;
- it does not conflict with a higher-confidence active fact;
- it is not a duplicate;
- any time-sensitive claim has an expiry.

Confirmation is required for:

- business decisions or commitments;
- prices, budgets, legal, financial, medical, licensing, or insurance claims;
- identity or ownership changes;
- instructions that would trigger external actions;
- conflicting evidence;
- low-confidence but potentially useful information.

Discarded content includes ads, navigation text, unsupported claims, duplicated snippets, secrets, and prompt-injection-like instructions found on pages.

## 9. Progressive Retrieval

The memory API exposes three layers:

### Index search

`GET /api/memory/search?q=...&limit=...`

Returns compact result IDs, summaries, types, timestamps, confidence, and source counts.

### Timeline

`GET /api/memory/timeline?event_id=...&before=...&after=...`

Returns nearby activity events without loading full detail for unrelated events.

### Full observations

`POST /api/memory/observations`

Accepts a bounded list of IDs and returns complete selected records and provenance.

Limits are enforced to prevent accidental full-memory injection into NVIDIA.

## 10. Real-Time Activity API

### SSE stream

`GET /api/activity/stream?after=<event-id>`

The server sends:

- ordered activity events;
- periodic heartbeat messages;
- event IDs for reconnection;
- no secrets or raw credentials.

SSE is selected instead of WebSocket because the flow is server-to-client, automatic browser reconnection is useful, and it reduces connection complexity.

### REST fallback

`GET /api/activity?request_id=...&after=...&limit=...`

The frontend uses this endpoint after reconnection or when SSE is unavailable.

The existing task progress endpoint remains compatible. Task runtime progress is bridged into the activity recorder rather than replaced.

## 11. Frontend Behavior

The frontend adds an activity store and a live panel. It shows no more than the most relevant active cards and preserves the existing panel limit.

User-facing states include:

- Entendiendo solicitud
- Consultando memoria
- Buscando en internet
- Revisando fuentes
- Analizando con NVIDIA
- Guardando conocimiento
- Esperando confirmación
- Completado
- Falló

Each completed web activity can reveal its sources. The UI never labels a failed or partial operation as completed.

## 12. Privacy and No-Store Controls

A redaction layer runs before event or memory persistence. It filters common API-key, token, credential, authorization-header, and password patterns.

The following controls are supported:

- request-level `no_store`;
- voice/text command “no guardes esta conversación”;
- explicit private markers;
- deletion of a fact and its non-required derived summaries;
- visibility of why a fact was stored.

Operational logs contain IDs and safe summaries, not raw secrets.

## 13. Error Handling

- Search unavailable: return a sourced-memory answer when possible; otherwise report that current information could not be checked.
- Individual source failure: continue with remaining sources and record the rejection.
- NVIDIA unavailable: return deterministic local results or gathered sources without fabricated analysis.
- SQLite busy: bounded retry; then a clear failed event.
- SSE disconnect: browser reconnects with the last event ID and REST fallback.
- Memory conflict: preserve both candidates, mark the conflict, and request confirmation when consequential.
- Expired fact: exclude from authoritative answers and optionally trigger fresh research.

No exception path may emit `request.completed`.

## 14. Compatibility and Migration

- Existing memory APIs remain operational during migration.
- Existing `TaskRegistry`, `TaskRouter`, and `TaskRuntime` contracts remain intact.
- Lead Hunter continues to use its provider and store; only its progress is mirrored into activity events initially.
- NVIDIA configuration remains unchanged.
- The first release does not migrate arbitrary existing memory into sourced facts automatically.
- Feature flags allow the router, web learning, and SSE panel to be enabled independently.

## 15. Testing Strategy

### Unit tests

- deterministic route selection;
- local responses bypass NVIDIA;
- memory-first behavior;
- source normalization and deduplication;
- learning-policy outcomes;
- secret redaction;
- expiry and conflict handling;
- monotonic event sequencing.

### Integration tests

- SQLite schema initialization and concurrent writes;
- web request from route through sourced answer and stored fact;
- NVIDIA/search failures never report completion;
- task-runtime events appear in activity history;
- SSE ordering, heartbeat, and reconnection;
- API pagination and bounded observation fetches.

### Frontend tests

- activity events map to visual states;
- failed work is labeled failed;
- reconnect resumes after the last event;
- sources are displayed only when present;
- no more than the allowed number of panels appears;
- ordinary conversation does not open unnecessary panels.

### Regression tests

All existing Python and frontend tests must pass before enabling any feature flag.

## 16. Delivery Sequence

1. Stabilize the existing voice baseline separately.
2. Add activity models and SQLite persistence.
3. Bridge existing task-runtime progress into activities.
4. Add progressive retrieval APIs.
5. Add deterministic fast routing.
6. Add web-provider abstraction and sourced research.
7. Add controlled learning and confirmation queue.
8. Add SSE and frontend activity panels.
9. Run complete regression, concurrency, privacy, and failure testing.
10. Enable features gradually in supervised mode.

Each step is independently testable and must be delivered through tests-first commits.

## 17. Success Criteria

The first version is successful when:

- deterministic requests return without an NVIDIA call;
- GEVER can answer from compact local memory;
- current-information requests include source provenance;
- safe web facts are stored with source, confidence, and expiry;
- consequential facts remain pending confirmation;
- the frontend displays ordered live activity;
- failed operations are never presented as completed;
- secrets are not persisted in tested cases;
- all existing and new tests pass;
- NVIDIA remains the configured primary reasoning model.
