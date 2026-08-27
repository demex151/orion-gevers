# GEVER Autonomous Visual Manager Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the fixed GEVER dashboard with an ambient sphere-and-background home plus up to three autonomous contextual panels, without changing working runtime behavior.

**Architecture:** Keep `App.jsx` mounted as the authoritative runtime for ORION, listening, conversation, barge-in, NVIDIA responses, Lead Hunter, memory, and `salir`. Refactor only the visible `HomeShell` presentation. Add a small pure Visual Manager state module and focused panel components; layout uses predefined safe slots rather than arbitrary coordinates.

**Tech Stack:** React, existing CSS, Node built-in test runner, existing Vite/Bun frontend build.

**Spec:** `docs/superpowers/specs/2026-08-27-visual-manager-ui-design.md`

## Global Constraints

- Preserve the exact current GEVER sphere/orb visual and asset URLs.
- Preserve the exact current background and fallback asset URL.
- Do not modify `frontend/src/App.jsx` runtime behavior.
- Do not modify ORION, microphone/listening, barge-in, NVIDIA/LLM, Lead Hunter, memory/backend, or `salir` behavior.
- Maximum simultaneous contextual panels: 3.
- Visual Manager failures must not block existing voice/runtime behavior.

---

### Task 1: Pure Visual Manager state

**Files:**
- Create: `frontend/src/visualManager.js`
- Create: `frontend/src/visualManager.test.js`

**Interfaces:**
- Produces: `createVisualState()`, `openPanel(state, panel)`, `updatePanel(state, id, patch)`, `minimizePanel(state, id)`, `closePanel(state, id)`, `closeAllPanels()`.
- Panel shape: `{ id, type, title, data, minimized, slot }`.

- [ ] Write tests proving a maximum of three panels, deterministic safe-slot assignment, replacement of the least-recent panel when full, update/minimize/close behavior, and immutable state transitions.
- [ ] Run `cd frontend && node --test src/visualManager.test.js` and verify RED because the module does not exist.
- [ ] Implement the minimal pure state module with slots `upper-right`, `lower-left`, `lower-right`.
- [ ] Run the test again and verify PASS.
- [ ] Commit only the Visual Manager module and tests.

### Task 2: Contextual panel renderer

**Files:**
- Create: `frontend/src/VisualPanel.jsx`
- Create: `frontend/src/VisualPanel.css`
- Create: `frontend/src/visualPanelModel.js`
- Create: `frontend/src/visualPanelModel.test.js`

**Interfaces:**
- Consumes: panel shape from Task 1.
- Produces: `VisualPanel({ panel })` and pure `normalizePanelContent(panel)` for presentation-safe rendering.

- [ ] Write model tests for agenda, leads, metrics, progress, communications, and generic structured content.
- [ ] Run model tests and verify RED.
- [ ] Implement normalization and the lightweight holographic renderer.
- [ ] Add CSS using transparency, subtle border/glow, depth, and short transitions; no sphere/background selectors may be overridden.
- [ ] Run model tests and frontend build.
- [ ] Commit panel renderer separately.

### Task 3: Ambient home shell

**Files:**
- Modify: `frontend/src/HomeShell.jsx`
- Modify: `frontend/src/HomeShellFix.css`
- Create: `frontend/src/homeVisualContract.test.js`

**Interfaces:**
- Consumes: current exact background constants and exact orb asset constants already in `HomeShell.jsx`.
- Consumes: Visual Manager state and `VisualPanel`.
- Preserves: hidden mounted `<App/>` runtime.

- [ ] Add a contract test that reads `HomeShell.jsx` and verifies the current background URLs and all current orb asset URLs remain present.
- [ ] Add contract assertions that fixed dashboard sections (`figma-os`, `figma-growth`, `figma-calendar`, `figma-comms`, `figma-agents`) are no longer rendered by the ambient home.
- [ ] Run contract test and verify RED on fixed-dashboard assertions.
- [ ] Refactor visible home markup to keep background, focus treatment, exact existing sphere markup/assets, minimal GEVER identity/status, and an empty contextual-panel stage.
- [ ] Remove only CSS for permanently visible dashboard chrome where safe; preserve orb/background rules byte-for-byte where practical.
- [ ] Run contract test and frontend build.
- [ ] Commit ambient shell separately.

### Task 4: Visual Manager integration with demo-safe commands

**Files:**
- Modify: `frontend/src/HomeShell.jsx`
- Create: `frontend/src/visualIntent.js`
- Create: `frontend/src/visualIntent.test.js`

**Interfaces:**
- Produces: `inferVisualIntent(text)` returning presentation-only actions such as `{ action: "open", type: "agenda" }` or `null`.
- Does not call calendar, network, Lead Hunter, or backend tools itself.

- [ ] Write tests for agenda/leads/metrics/progress visual intents and unrelated text returning `null`.
- [ ] Run and verify RED.
- [ ] Implement conservative presentation-only intent mapping.
- [ ] Wire typed HomeShell commands to open/update demo-safe contextual panels after the existing `/api/chat` response without altering the request or speech path.
- [ ] Ensure visual errors are caught independently and never fail `sendCommand()` or speech.
- [ ] Run visual tests and frontend build.
- [ ] Commit integration separately.

### Task 5: Regression verification

**Files:**
- No production changes unless a regression is found.

- [ ] Run `cd frontend && node --test src/bargeInController.test.js src/speechPlayback.test.js src/globalAudioBargeIn.test.js src/visualManager.test.js src/visualPanelModel.test.js src/homeVisualContract.test.js src/visualIntent.test.js`.
- [ ] Run the existing frontend production build command from `frontend/package.json` or repository scripts and verify success.
- [ ] From repository root run `py -m pytest -v` and verify the existing Python suite remains green.
- [ ] Manually smoke-test ORION activation, normal conversation, speaking over GEVER, `salir`, and Lead Hunter.
- [ ] Visually confirm the sphere and background are unchanged and that the base screen contains no permanent dashboard cards.
- [ ] Commit only if verification required a targeted regression fix.
