# GEVER Real Runtime Tools Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make microphone capture terminate reliably and make spoken client-search commands execute the existing Lead Hunter V2 pipeline.

**Architecture:** Keep voice capture, command routing, and Lead Hunter execution separated. `GeversListener` owns safe finite capture defaults; `GeversBrain` routes explicit lead-search commands to a focused adapter while all other requests continue to NVIDIA.

**Tech Stack:** Python 3.13, SpeechRecognition, existing GEVER Lead Hunter V2, pytest, NVIDIA OpenAI-compatible client.

**Spec:** `docs/superpowers/specs/2026-08-26-gever-real-runtime-tools-design.md`

## Global Constraints
- Keep Lead Hunter V2 evaluation/filter behavior unchanged.
- Keep NVIDIA as the normal conversational provider.
- Do not add Nextdoor integration or automated outreach.
- Never fabricate a lead when the search returns zero accepted opportunities.

---

### Task 1: Finite microphone capture

**Files:**
- Modify: `gever/listen.py`
- Modify: `backend/server.py`
- Create: `tests/test_listener_runtime.py`

**Interfaces:**
- Consumes: `GeversListener.listen(timeout=None, phrase_time_limit=None)`
- Produces: safe finite effective defaults while preserving explicit caller values.

- [ ] **Step 1: Write failing tests** that use fake recognizer/microphone objects and assert a default call reaches `recognizer.listen` with finite timeout and phrase-time-limit values; assert explicit caller values are preserved.
- [ ] **Step 2: Run** `py -m pytest tests/test_listener_runtime.py -v` and confirm failure on current unlimited defaults.
- [ ] **Step 3: Implement minimal safe defaults** in `GeversListener.listen` and stop the backend endpoint from explicitly overriding them with `None`.
- [ ] **Step 4: Run** `py -m pytest tests/test_listener_runtime.py -v` and confirm pass.
- [ ] **Step 5: Commit** `fix: bound GEVER microphone capture`.

### Task 2: Deterministic Lead Hunter command routing

**Files:**
- Create: `gever/tools/__init__.py`
- Create: `gever/tools/lead_hunter_tool.py`
- Modify: `gever/brain.py`
- Create: `tests/test_brain_tools.py`

**Interfaces:**
- Produces: `is_lead_hunter_request(text: str) -> bool`
- Produces: `run_lead_hunter_tool() -> str`
- `GeversBrain.think()` returns the tool result before calling NVIDIA when intent matches.

- [ ] **Step 1: Write failing routing tests** for `busca oportunidades de clientes para Gevers Painting`, `busca clientes de pintura`, `buscar leads`, and a normal conversational sentence that must not route.
- [ ] **Step 2: Run** `py -m pytest tests/test_brain_tools.py -v` and confirm failure.
- [ ] **Step 3: Implement the intent matcher and adapter** using the existing Lead Hunter classes/configuration rather than duplicating evaluator logic.
- [ ] **Step 4: Add tests for zero accepted leads** and accepted leads using injected/fake hunter results so tests never require internet.
- [ ] **Step 5: Modify `GeversBrain.think()`** to execute the tool before NVIDIA only for matching requests.
- [ ] **Step 6: Run** `py -m pytest tests/test_brain_tools.py -v` and confirm pass.
- [ ] **Step 7: Commit** `feat: connect GEVER brain to Lead Hunter`.

### Task 3: Regression and real-runtime verification

**Files:**
- Modify only if a regression is demonstrated by tests.

**Interfaces:**
- Consumes the completed voice and tool-routing behavior.

- [ ] **Step 1: Run full suite** with `py -m pytest -v` and require zero failures.
- [ ] **Step 2: Start API** with `py -m uvicorn backend.server:app --host 127.0.0.1 --port 8000`.
- [ ] **Step 3: Verify voice capture** by speaking one sentence and confirming capture terminates after silence.
- [ ] **Step 4: Say** `GEVER, busca oportunidades de clientes para Gevers Painting` and confirm Lead Hunter executes.
- [ ] **Step 5: Confirm zero-result behavior** says no valid recent opportunities were found rather than inventing leads.
- [ ] **Step 6: Confirm ordinary conversation** still reaches NVIDIA.
- [ ] **Step 7: Commit any test-backed corrections**, then open a PR to `main`.