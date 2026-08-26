# GEVER Home Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild only GEVER's Home screen to closely match the supplied futuristic UI references while preserving the working ORION, chat, TTS, subtitle and navigation behavior.

**Architecture:** Keep the current React/Vite application and backend API unchanged. Restructure only Home presentation in `App.jsx`, preserve behavior-critical functions/refs, and replace Home styling in `App.css` with scoped futuristic dashboard styles so secondary pages remain usable.

**Tech Stack:** React, Vite, CSS, existing FastAPI backend.

**Spec:** `docs/superpowers/specs/2026-08-25-home-redesign-design.md`

## Global Constraints
- Redesign only `Inicio` in this phase.
- Preserve API base `http://127.0.0.1:8000` and all existing backend contracts.
- Preserve ORION wake, manual talk, chat, TTS, subtitles, conversation state, memory and navigation wiring.
- Do not modify backend/server or `gever/` logic.
- Do not introduce new runtime dependencies for the visual redesign.
- Keep static decorative metrics isolated from future real-data wiring.

---

### Task 1: Preserve behavior while restructuring Home markup

**Files:**
- Modify: `frontend/src/App.jsx`

**Interfaces:**
- Consumes: existing state (`status`, `conversationMode`, `isListening`, `isSending`, `subtitles`) and existing handlers such as Home navigation and manual talk.
- Produces: scoped Home DOM classes consumed by `App.css` without changing backend requests.

- [ ] **Step 1: Inventory behavior-critical Home handlers and refs**
Confirm the existing Home controls reference existing functions and that no voice/chat/controller function is renamed or removed.

- [ ] **Step 2: Restructure only the Home render tree**
Create a clear Home hierarchy: top header, hero/core area, operational panel, lower status/metric cards and existing interaction surfaces. Keep non-Home render branches intact.

- [ ] **Step 3: Bind visual state to existing runtime state**
Map waiting/listening/thinking/preparing-voice/speaking states to classes and labels without changing controller behavior.

- [ ] **Step 4: Verify source-level wiring**
Search the modified file for the existing API endpoints `/api/chat`, `/api/tts`, `/api/wake-listen`, memory handling, controller loop and manual-talk handler; verify they remain present and referenced.

- [ ] **Step 5: Commit**
Commit with message `feat: restructure GEVER home dashboard`.

### Task 2: Reproduce the reference Home visual system

**Files:**
- Modify: `frontend/src/App.css`

**Interfaces:**
- Consumes: Home class names from Task 1.
- Produces: desktop-first responsive visual system with no JavaScript dependency.

- [ ] **Step 1: Establish Home design tokens**
Define scoped values for near-black surfaces, cyan/blue glow, violet accent, muted text, luminous borders, panel radii and spacing.

- [ ] **Step 2: Build the dashboard shell**
Style sidebar, topbar and Home content grid to reproduce the reference proportions and visual density.

- [ ] **Step 3: Build the GEVER core**
Create the concentric rings, orbital marks, central luminous core, subtle grid and state-reactive glow using CSS pseudo-elements and keyframes.

- [ ] **Step 4: Build operational and lower cards**
Match glass surfaces, borders, compact labels, indicators, progress treatments and lower-card hierarchy from the reference while keeping decorative values clearly isolated.

- [ ] **Step 5: Add responsive behavior**
At narrower widths, collapse the Home grid cleanly without covering controls or breaking navigation.

- [ ] **Step 6: Commit**
Commit with message `style: match futuristic GEVER home reference`.

### Task 3: Build and regression verification

**Files:**
- Verify: `frontend/src/App.jsx`
- Verify: `frontend/src/App.css`
- Verify: `frontend/package.json`

**Interfaces:**
- Consumes: Tasks 1-2.
- Produces: buildable Home redesign with existing interaction wiring preserved.

- [ ] **Step 1: Install existing frontend dependencies if needed**
Run `npm ci` from `frontend/`; do not add dependencies.

- [ ] **Step 2: Build**
Run `npm run build` from `frontend/`. Expected: Vite build exits successfully.

- [ ] **Step 3: Review behavior-critical diff**
Verify the diff does not alter backend Python files, API endpoint strings, wake/controller logic, TTS implementation or memory implementation.

- [ ] **Step 4: Review visual hierarchy**
Compare the rendered Home against the supplied reference: sidebar width, header hierarchy, dominant central core, right panel, lower cards, cyan/violet lighting, dark surfaces and spacing.

- [ ] **Step 5: Final commit if verification required adjustments**
Commit verification fixes with message `fix: finalize GEVER home redesign`.
