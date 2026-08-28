# GEVER Task Runtime Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a modular Task Registry/Router/Runtime and migrate Lead Hunter through it without changing GEVER's user-visible behavior.

**Architecture:** `GeversBrain` delegates task commands to a deterministic router. Registered capabilities execute through a runtime that owns lifecycle and verification. Lead Hunter becomes the first capability while retaining existing telemetry/store/results behavior.

**Tech Stack:** Python 3.13, dataclasses, pytest, existing FastAPI/GEVER modules.

**Spec:** `docs/superpowers/specs/2026-08-28-task-runtime-design.md`

## Global Constraints
- Preserve ORION, TTS, microphone, barge-in, NVIDIA, memory, Lead Hunter telemetry, graph commands, and stored results.
- No new external dependencies.
- Non-task conversation continues through NVIDIA.
- Existing tests must remain green.

---

### Task 1: Core task contracts, registry and router

**Files:**
- Create: `gever/tasks/__init__.py`
- Create: `gever/tasks/models.py`
- Create: `gever/tasks/registry.py`
- Create: `gever/tasks/router.py`
- Test: `tests/test_task_registry_router.py`

**Interfaces:**
- Produces: `TaskStatus`, `TaskOutcome`, `Capability`, `TaskRegistry.register/get/resolve`, `TaskRouter.route(text)`.

- [ ] Write tests proving registration, duplicate rejection, deterministic matching, and `None` for conversation.
- [ ] Run `py -m pytest tests/test_task_registry_router.py -v` and confirm failure before implementation.
- [ ] Implement dataclasses/protocol-style base capability, registry, and router with normalized Spanish matching.
- [ ] Re-run focused tests and confirm PASS.
- [ ] Commit the task.

### Task 2: Task Runtime lifecycle and verification

**Files:**
- Create: `gever/tasks/runtime.py`
- Test: `tests/test_task_runtime.py`

**Interfaces:**
- Consumes: `Capability`, `TaskOutcome`, `TaskStatus`.
- Produces: `TaskRuntime.run(capability, context) -> TaskOutcome` and `TaskRuntime.last_outcome`.

- [ ] Write tests for successful execution, verification failure, exception containment, unique task IDs, and lifecycle timestamps.
- [ ] Run `py -m pytest tests/test_task_runtime.py -v` and confirm failure.
- [ ] Implement runtime with `started -> running -> verifying -> completed/failed` semantics and exception containment.
- [ ] Re-run focused tests and confirm PASS.
- [ ] Commit the task.

### Task 3: Lead Hunter capability

**Files:**
- Create: `gever/tasks/capabilities/__init__.py`
- Create: `gever/tasks/capabilities/lead_hunter.py`
- Test: `tests/test_lead_hunter_capability.py`

**Interfaces:**
- Consumes: existing hunter/store factories and `lead_hunter_telemetry.publish`.
- Produces: `LeadHunterCapability.execute(context)`, `verify(summary)`, `format_response(summary)`.

- [ ] Write tests using fake hunter summaries for zero-result and accepted-result paths and verify progress callback wiring.
- [ ] Run focused test and confirm failure.
- [ ] Implement capability without changing `gever/leads/*`.
- [ ] Re-run focused test and confirm PASS.
- [ ] Commit the task.

### Task 4: Integrate runtime into GeversBrain

**Files:**
- Modify: `gever/brain.py`
- Test: `tests/test_brain_task_runtime.py`
- Existing regression tests: `tests/test_brain_lead_hunter_tool.py`, `tests/test_brain_lead_results_tool.py`, `tests/test_brain_language_and_graph_commands.py`, `tests/test_brain_answer_cleanup.py`

**Interfaces:**
- `GeversBrain.__init__` constructs registry/router/runtime and registers Lead Hunter capability.
- `_run_lead_hunter()` remains as compatibility wrapper.
- `think()` asks router before NVIDIA conversation, while graph/results commands retain precedence.

- [ ] Write integration tests proving Lead Hunter routes through runtime and ordinary Spanish conversation is not routed.
- [ ] Run focused integration/regression tests and confirm new test fails before implementation.
- [ ] Modify `brain.py` minimally, preserving response strings and existing helper methods.
- [ ] Run all listed brain tests and confirm PASS.
- [ ] Commit the task.

### Task 5: Full regression verification

**Files:** No production changes unless a regression is discovered.

- [ ] Run `py -m pytest -v`.
- [ ] Confirm every existing and new Python test passes.
- [ ] Run current frontend tests for voice/visual regressions: `node --test src/bargeInController.test.js src/speechPlayback.test.js src/globalAudioBargeIn.test.js src/visualManager.test.js src/visualPanelModel.test.js src/visualIntent.test.js src/leadResultsPanels.test.js src/leadPanelSpeechLifecycle.test.js` from `frontend`.
- [ ] Confirm frontend tests pass without modifying frontend production files.
- [ ] Review diff to ensure no ORION/TTS/barge-in/frontend behavior changed.
