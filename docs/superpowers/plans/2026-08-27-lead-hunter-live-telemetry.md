# Lead Hunter Live Telemetry Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stream real Lead Hunter work into temporary contextual graphics around GEVER's sphere without changing hunt decisions or voice behavior.

**Architecture:** Add optional progress emission to the existing synchronous Lead Hunter, aggregate it in a thread-safe backend telemetry broker, expose snapshots through a read-only API, and let the frontend poll and translate active snapshots into Visual Manager panels. Telemetry is strictly observational and failure-isolated.

**Tech Stack:** Python 3.13, FastAPI, React, Node built-in test runner, existing Visual Manager.

**Spec:** `docs/superpowers/specs/2026-08-27-lead-hunter-live-telemetry-design.md`

## Global Constraints
- Real activity only; no simulated progress.
- Do not alter evaluator acceptance/rejection logic.
- Do not alter ORION, microphone, barge-in, TTS, NVIDIA/brain, memory, or `salir` behavior.
- Preserve exact ambient background and sphere.
- Telemetry failure must never fail Lead Hunter.

---

### Task 1: Lead Hunter progress events
**Files:** Modify `gever/leads/hunter.py`; create `tests/test_lead_hunter_progress.py`.
- [ ] Write failing tests for start/search/finding/rejection/duplicate/accepted/saved/completed events and callback failure isolation.
- [ ] Run targeted tests and verify RED.
- [ ] Add optional `progress_callback=None` to `LeadHunter.run` and a private safe emitter.
- [ ] Emit only facts known at each existing decision point; preserve current run summary behavior.
- [ ] Run targeted and existing Lead Hunter tests; verify PASS.

### Task 2: Telemetry broker and rejection categories
**Files:** Create `gever/leads/telemetry.py`; create `tests/test_lead_telemetry.py`.
- [ ] Write failing tests for thread-safe snapshot aggregation and rejection reason mapping to competition/directories/advertising/contractors/stale/other.
- [ ] Implement broker with immutable snapshot copies and bounded last-event data.
- [ ] Verify counts for found/analyzed/rejected/valid/duplicates/saved and HOT/WARM/PROSPECT.
- [ ] Run tests; verify PASS.

### Task 3: Wire real hunts and expose read-only API
**Files:** Modify the Lead Hunter construction/wiring used by `gever/brain.py`; modify `backend/server.py`; create/extend backend tests.
- [ ] Write failing integration test proving a voice/chat-triggered hunt updates the broker.
- [ ] Write failing API test for `GET /api/lead-hunter/progress` idle/active/completed snapshots.
- [ ] Wire the broker callback into the existing real Lead Hunter instance without changing command recognition.
- [ ] Add read-only progress endpoint.
- [ ] Run brain tool, Lead Hunter and backend tests; verify PASS.

### Task 4: Frontend telemetry model
**Files:** Create `frontend/src/leadHunterTelemetry.js`; create `frontend/src/leadHunterTelemetry.test.js`.
- [ ] Write failing tests converting backend snapshots to pipeline/counters/results panel models.
- [ ] Include ten visible workflow labels while deriving completion from real snapshot facts.
- [ ] Ensure idle snapshot returns no panels.
- [ ] Implement minimal pure transformation.
- [ ] Run Node test; verify PASS.

### Task 5: Temporary live task workspace
**Files:** Modify `frontend/src/HomeShell.jsx`; modify `frontend/src/VisualPanel.jsx`; modify `frontend/src/VisualPanel.css`; optionally create focused `LeadHunterLivePanels.jsx`.
- [ ] Add frontend test/controller test for polling lifecycle: idle -> active -> completed -> clear.
- [ ] Poll the read-only endpoint only while the app is mounted; tolerate network failures silently.
- [ ] Feed up to three panels through existing Visual Manager safe slots.
- [ ] Render pipeline stage activity, live rejection/count bars, HOT/WARM/PROSPECT result distribution.
- [ ] Keep centered sphere visible and unobstructed.
- [ ] Auto-clear completed task panels after a short display period.
- [ ] Run frontend tests/build; verify PASS.

### Task 6: Full regression verification
- [ ] Run all Lead Hunter/evaluator/brain Python tests.
- [ ] Run `py -m pytest -v`.
- [ ] Run frontend barge-in, speech playback, global audio, orb, Visual Manager, and telemetry tests.
- [ ] Run frontend production build.
- [ ] Manual smoke test: ORION -> "busca clientes de pintura" -> live real graphics -> spoken final result -> `salir` -> ambient sphere-only home.
- [ ] Confirm speaking over GEVER still interrupts audio immediately.
