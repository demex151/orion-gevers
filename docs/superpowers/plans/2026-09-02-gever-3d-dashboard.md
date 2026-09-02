# GEVER 3D Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current image-composited GEVER home visual with the approved HUD and a genuine real-time 3D GEVER core while preserving working chat, TTS, voice state, agents, memory, and backend behavior.

**Architecture:** Keep application behavior behind `HomeShell.jsx`/`geverVisualBridge.js`, add a small normalized visual-state layer, and render the central scene with React Three Fiber. Keep dashboard chrome as DOM/CSS so the HUD remains accessible and responsive and so continuous WebGL animation does not cause React dashboard re-renders.

**Tech Stack:** React 19, Vite 8, Three.js, `@react-three/fiber`, `@react-three/drei`, existing Node tests/oxlint.

**Spec:** `docs/plans/2026-09-02-gever-3d-dashboard-design.md`

## Global Constraints

- The approved reference is the target layout, not merely inspiration.
- The central visual must be real-time 3D, not a static image or video.
- Preserve `/api/chat`, `/api/tts`, existing voice status integration, memory, agents, and required navigation behavior.
- Keep the legacy application available as a temporary fallback during migration.
- Camera/hand-tracking code must not directly mutate Three.js objects.
- Keep dashboard panels as DOM; WebGL owns the central core scene only.

---

### Task 1: Normalize GEVER visual states

**Files:**
- Create: `frontend/src/coreState.js`
- Create: `frontend/src/coreState.test.js`
- Modify: `frontend/src/geverVisualBridge.js`

**Interfaces:**
- Produces: `normalizeCoreState(status: string): "idle"|"listening"|"thinking"|"speaking"|"working"|"error"`
- Produces: visual bridge detail property `coreState`

- [ ] **Step 1: Write failing tests for status normalization** covering empty/esperando→idle, escuchando→listening, pensando→thinking, hablando→speaking, procesando/trabajando→working, error→error.
- [ ] **Step 2: Run** `cd frontend && node --test src/coreState.test.js` **and verify failure because the module does not exist.**
- [ ] **Step 3: Implement `normalizeCoreState`** as a pure lowercase/accent-tolerant mapping with `idle` fallback.
- [ ] **Step 4: Extend `buildVisualState`** to return the existing fields plus `coreState: normalizeCoreState(status)` without removing existing properties.
- [ ] **Step 5: Run** `node --test src/coreState.test.js src/geverVisualBridge.test.js` **and verify PASS.**
- [ ] **Step 6: Commit** `feat: normalize GEVER visual core states`.

### Task 2: Add the 3D runtime and isolated core scene

**Files:**
- Modify: `frontend/package.json`
- Modify: `frontend/package-lock.json`
- Create: `frontend/src/components/core3d/GeverCore3D.jsx`
- Create: `frontend/src/components/core3d/EnergyCore.jsx`
- Create: `frontend/src/components/core3d/HolographicRings.jsx`
- Create: `frontend/src/components/core3d/OrbitLines.jsx`
- Create: `frontend/src/components/core3d/ParticleField.jsx`
- Create: `frontend/src/components/core3d/CoreStateController.js`
- Create: `frontend/src/components/core3d/CoreStateController.test.js`

**Interfaces:**
- Consumes: normalized `coreState`
- Produces: `getCoreMotionProfile(coreState)` with numeric `rotationSpeed`, `pulse`, `particleEnergy`, `orbitSpeed`, `scale`
- Produces: `<GeverCore3D coreState={...} />`

- [ ] **Step 1: Add failing controller tests** asserting idle has the calmest motion, thinking/working increase orbital activity, speaking increases pulse, and error has a deterministic warning profile.
- [ ] **Step 2: Run controller test and verify failure.**
- [ ] **Step 3: Install** `three`, `@react-three/fiber`, and `@react-three/drei` **with npm so both package files are updated.**
- [ ] **Step 4: Implement `getCoreMotionProfile`** as a pure function with explicit profiles for all six states.
- [ ] **Step 5: Implement `EnergyCore`** using sphere geometry and emissive/translucent material; animate scale/pulse through refs in `useFrame`.
- [ ] **Step 6: Implement `HolographicRings`** as multiple independently tilted torus/ring groups with separate speeds.
- [ ] **Step 7: Implement `OrbitLines`** as thin orbital curves/rings around the energy core.
- [ ] **Step 8: Implement `ParticleField`** using a bounded point cloud generated once with `useMemo`, animated with refs rather than React state.
- [ ] **Step 9: Implement `GeverCore3D`** with `<Canvas>`, perspective camera, lights, scene groups, graceful DOM fallback text if WebGL creation fails, and no backend calls.
- [ ] **Step 10: Run** `node --test src/components/core3d/CoreStateController.test.js` **and `npm run build`; verify both PASS.**
- [ ] **Step 11: Commit** `feat: add real-time GEVER 3D core`.

### Task 3: Replace the Figma orb without changing command behavior

**Files:**
- Modify: `frontend/src/HomeShell.jsx`
- Modify: `frontend/src/HomeShellFix.css`
- Test: existing `frontend/src/geverVisualBridge.test.js`, `frontend/src/speechVisuals.test.js`, `frontend/src/viewportScale.test.js` if present

**Interfaces:**
- Consumes: `<GeverCore3D coreState>`
- Preserves: `sendCommand()`, `speak()`, `/api/chat`, `/api/tts`

- [ ] **Step 1: Add a small testable state helper/subscription if needed** so `HomeShell` can receive `GEVER_VISUAL_EVENT` and expose the normalized state without duplicating normalization logic.
- [ ] **Step 2: Run the relevant test and verify failure before implementation.**
- [ ] **Step 3: Remove only the central Figma orb image composition constants/elements** (`ORB_*` and their `<img>` layers); leave unrelated shell behavior intact.
- [ ] **Step 4: Mount `<GeverCore3D coreState={coreState} />`** in the same central visual region.
- [ ] **Step 5: Map local typed-command transitions** to thinking/speaking/listening immediately while preserving bridge-driven status when voice runtime updates arrive.
- [ ] **Step 6: Update central-container CSS** for genuine perspective space and responsive sizing; do not recreate the core with CSS images.
- [ ] **Step 7: Run all frontend Node tests, `npm run lint`, and `npm run build`; verify PASS.**
- [ ] **Step 8: Commit** `feat: connect GEVER runtime to 3D core`.

### Task 4: Extract and reproduce the approved HUD panels

**Files:**
- Create: `frontend/src/components/dashboard/Sidebar.jsx`
- Create: `frontend/src/components/dashboard/GreetingHeader.jsx`
- Create: `frontend/src/components/dashboard/SystemMetrics.jsx`
- Create: `frontend/src/components/dashboard/ActiveAgents.jsx`
- Create: `frontend/src/components/dashboard/GesturePanel.jsx`
- Create: `frontend/src/components/dashboard/CommandBar.jsx`
- Create: `frontend/src/components/dashboard/SystemFooter.jsx`
- Create: `frontend/src/styles/gever-dashboard.css`
- Modify: `frontend/src/HomeShell.jsx`

**Interfaces:**
- `Sidebar({activeSection,onNavigate})`
- `SystemMetrics({cpu,memory,network,status})`
- `ActiveAgents({agents})`
- `GesturePanel({enabled,lastGesture})`
- `CommandBar({value,onChange,onSubmit,busy})`
- `SystemFooter({coreState,status})`

- [ ] **Step 1: Extract the command input into `CommandBar`** with the same Enter/button semantics currently in `HomeShell`.
- [ ] **Step 2: Extract sidebar navigation** while preserving `openSection`/legacy fallback behavior.
- [ ] **Step 3: Build system metrics panel** in the approved compact holographic style; keep values supplied through props so real telemetry can replace defaults later.
- [ ] **Step 4: Build active-agents panel** from the existing agent data and preserve status indicators.
- [ ] **Step 5: Build gesture panel** showing camera/gesture readiness without pretending gesture recognition is active when it is not.
- [ ] **Step 6: Build greeting/header and footer status components.**
- [ ] **Step 7: Recompose `HomeShell`** into left rail + metrics, dominant center core, right agents/gesture panels, command region, and footer matching the approved reference proportions.
- [ ] **Step 8: Implement `gever-dashboard.css`** with dark HUD background, cyan holographic borders, fine grid/technical markings, restrained glow, responsive breakpoints, and no generic SaaS card styling.
- [ ] **Step 9: Run `npm run lint` and `npm run build`; verify PASS.**
- [ ] **Step 10: Commit** `feat: rebuild GEVER dashboard HUD`.

### Task 5: Add gesture-controller boundary

**Files:**
- Create: `frontend/src/gestures/gestureCommands.js`
- Create: `frontend/src/gestures/gestureCommands.test.js`
- Modify: `frontend/src/components/core3d/GeverCore3D.jsx`
- Modify: `frontend/src/components/dashboard/GesturePanel.jsx`

**Interfaces:**
- Produces: `GEVER_GESTURE_EVENT = "gever:gesture-command"`
- Produces: `publishGestureCommand({type,value})`
- Supported command types: `rotate`, `zoom`, `select`, `open-panel`, `close-panel`, `reset-view`

- [ ] **Step 1: Write failing tests** that reject unknown commands and normalize supported command payloads.
- [ ] **Step 2: Run test and verify failure.**
- [ ] **Step 3: Implement pure validation/normalization plus browser event publishing.**
- [ ] **Step 4: Subscribe in `GeverCore3D`** and translate normalized commands into target rotation/zoom refs; do not import camera or MediaPipe code into the scene.
- [ ] **Step 5: Update `GesturePanel`** to display `Prepared`/last command while real camera tracking remains a separate phase.
- [ ] **Step 6: Run gesture tests plus full frontend tests/build; verify PASS.**
- [ ] **Step 7: Commit** `feat: add GEVER gesture control boundary`.

### Task 6: Regression verification and visual acceptance

**Files:**
- Modify only files required to fix verified regressions.

**Interfaces:**
- Validates all prior tasks.

- [ ] **Step 1: Run** `cd frontend && node --test src/*.test.js src/components/core3d/*.test.js src/gestures/*.test.js` **and verify PASS.**
- [ ] **Step 2: Run** `npm run lint` **and verify zero errors.**
- [ ] **Step 3: Run** `npm run build` **and verify production build succeeds.**
- [ ] **Step 4: Run the repository backend test suite from repo root** using its documented pytest environment and verify no regressions from frontend work.
- [ ] **Step 5: Start backend and frontend locally and verify** chat submission reaches `/api/chat`, TTS reaches `/api/tts`, the core transitions through thinking/speaking/listening, legacy fallback navigation still opens, and the dashboard remains usable if the 3D canvas cannot initialize.
- [ ] **Step 6: Visually compare against the approved reference** at desktop width: left navigation/metrics, dominant central 3D core, right agents/gestures, command region, and system footer must all be present with the intended holographic depth.
- [ ] **Step 7: Verify responsive layout** at a narrow viewport without overlapping the command input or making navigation inaccessible.
- [ ] **Step 8: Commit any verified fixes** with a focused `fix:` commit; if no fixes are needed, do not create an empty commit.
