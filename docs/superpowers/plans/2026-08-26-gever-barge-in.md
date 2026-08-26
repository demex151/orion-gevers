# GEVER Barge-In Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let the user interrupt GEVER naturally during browser TTS playback, stop the current answer, and process the interrupting speech exactly once as the next conversation turn.

**Architecture:** Add an isolated browser-side barge-in detector that exists only while TTS is playing. Make the existing audio playback cancellable, then let `HomeShell` coordinate playback and interruption without creating a second permanent conversation loop or changing backend session/chat/TTS semantics.

**Tech Stack:** React, browser MediaDevices/Web Audio APIs, existing frontend session client and browser audio playback helper, Vitest.

**Spec:** `docs/superpowers/specs/2026-08-26-gever-barge-in-design.md`

## Global Constraints

- Do not alter wake-word activation, the backend session state machine, `/api/chat`, `/api/tts` generation, memory behavior, or browser-only TTS ownership.
- Do not restore Windows Media Player/local backend playback.
- The hidden legacy React controller must not own the microphone.
- Any real user speech during GEVER playback may interrupt; saying `ORION` is not required during an active session.
- Barge-in failure must fall back to the current behavior rather than breaking conversation.
- All microphone streams, AudioContexts, timers, and listeners created for barge-in must be released on stop/unmount/session close.

---

### Task 1: Cancellable Browser Playback

**Files:**
- Modify: `frontend/src/audioPlayback.js`
- Test: `frontend/src/audioPlayback.test.js`

**Interfaces:**
- Produces: `playAudioBlob(blob, options)` returning a Promise with the existing result plus support for `options.signal: AbortSignal`.
- Behavior: abort pauses the active `Audio`, resets its current time when possible, revokes the object URL, and resolves as `{ interrupted: true }` rather than throwing a connection error.

- [ ] **Step 1: Add failing tests for cancellation**

Add tests that mock `Audio`, `URL.createObjectURL`, and an `AbortController`; start playback, abort it, and assert `pause()` is called exactly once and the result contains `interrupted: true`. Preserve existing autoplay-blocked tests.

- [ ] **Step 2: Run the focused test**

Run: `cd frontend && npm test -- --run src/audioPlayback.test.js`

Expected: the new cancellation test fails because playback does not yet consume an AbortSignal.

- [ ] **Step 3: Implement minimal AbortSignal support**

In `playAudioBlob`, register one abort handler before `audio.play()`. The handler must call `audio.pause()`, attempt `audio.currentTime = 0`, clean up listeners/object URL once, and settle the Promise with `{ interrupted: true }`. Remove the abort listener during all normal completion/error cleanup paths.

- [ ] **Step 4: Run the focused test again**

Run: `cd frontend && npm test -- --run src/audioPlayback.test.js`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/audioPlayback.js frontend/src/audioPlayback.test.js
git commit -m "feat: make GEVER browser audio interruptible"
```

### Task 2: Isolated Barge-In Detector

**Files:**
- Create: `frontend/src/bargeInController.js`
- Create: `frontend/src/bargeInController.test.js`

**Interfaces:**
- Produces: `createBargeInController(deps?)`.
- Returned controller exposes `start({ onSpeech })` and `stop()`.
- `start` requests microphone audio with `{ echoCancellation:true, noiseSuppression:true, autoGainControl:true }`.
- `onSpeech` fires at most once per `start` cycle after sustained voice-like activity; it receives the captured interruption text when browser speech recognition is available, otherwise it signals interruption and lets HomeShell use the existing session listen capture immediately after playback stops.

- [ ] **Step 1: Write detector lifecycle tests**

Test that `start` requests the expected audio constraints, transient activity below the confirmation window does not fire, sustained activity fires once, and `stop` stops every MediaStream track and closes the AudioContext.

- [ ] **Step 2: Run the detector tests**

Run: `cd frontend && npm test -- --run src/bargeInController.test.js`

Expected: FAIL because the module does not exist.

- [ ] **Step 3: Implement the detector**

Create a controller using `navigator.mediaDevices.getUserMedia`, an `AudioContext`, `MediaStreamAudioSourceNode`, and `AnalyserNode`. Sample RMS amplitude on a timer. Require sustained activity across a short confirmation interval instead of one spike. Prefer browser `SpeechRecognition`/`webkitSpeechRecognition` when present to retain the utterance. Keep all thresholds/constants local to this module so sensitivity can be tuned without changing session code.

- [ ] **Step 4: Implement deterministic cleanup**

`stop()` must clear the sampling timer, stop recognition if active, stop all stream tracks, disconnect audio nodes, close the AudioContext, and make repeated `stop()` calls harmless.

- [ ] **Step 5: Run detector tests**

Run: `cd frontend && npm test -- --run src/bargeInController.test.js`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/bargeInController.js frontend/src/bargeInController.test.js
git commit -m "feat: detect user speech during GEVER playback"
```

### Task 3: Integrate Barge-In Into the Existing Session Loop

**Files:**
- Modify: `frontend/src/HomeShell.jsx`
- Modify or create focused tests using the repository's existing HomeShell/session testing pattern.

**Interfaces:**
- Consumes: cancellable `playAudioBlob(..., { signal })` and `createBargeInController()`.
- Produces: `speak(text)` result that distinguishes normal completion from `{ interrupted: true, text?: string }`.
- The conversation loop consumes an interrupted utterance before opening another `sessionClient.listen()` call.

- [ ] **Step 1: Add failing integration tests**

Cover these cases: normal TTS completion returns to the existing listen loop; confirmed interruption aborts playback once; captured interruption text goes to `/api/chat` exactly once; interruption without retained text causes exactly one normal session listen after audio stops; session close/unmount stops the detector.

- [ ] **Step 2: Run the focused HomeShell/session tests**

Run the repository's frontend test command targeting the new/modified HomeShell tests.

Expected: FAIL because `HomeShell` does not yet coordinate interruption.

- [ ] **Step 3: Add barge-in refs without changing existing session ownership**

Add refs for the active playback `AbortController`, barge-in controller, and one pending interrupted utterance. Do not add a second permanent conversation loop.

- [ ] **Step 4: Wrap only the TTS playback window**

Inside `speak(text)`, start barge-in immediately before browser playback and stop it in `finally`. On confirmed speech, abort the active playback. Return interruption as expected control flow, not an error.

- [ ] **Step 5: Feed interruption into the next existing turn**

At the top of each conversation-loop iteration, consume pending interruption text if present; otherwise call the existing `sessionClient.listen()`. This guarantees the interrupting phrase is processed once and avoids simultaneous normal microphone ownership.

- [ ] **Step 6: Preserve fallback behavior**

If barge-in initialization fails because microphone/Web Audio/SpeechRecognition is unavailable, log a warning and let GEVER finish speaking. The existing post-TTS listen loop must continue unchanged.

- [ ] **Step 7: Run focused tests**

Run the HomeShell/session tests plus `audioPlayback.test.js` and `bargeInController.test.js`.

Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add frontend/src/HomeShell.jsx frontend/src/audioPlayback.js frontend/src/bargeInController.js frontend/src/*test.js
git commit -m "feat: allow natural voice interruption while GEVER speaks"
```

### Task 4: Regression Verification

**Files:**
- Verify only; no production changes unless a failing regression demonstrates a scoped defect.

**Interfaces:**
- Existing backend and frontend contracts must remain unchanged.

- [ ] **Step 1: Run the complete frontend test suite**

Run: `cd frontend && npm test -- --run`

Expected: PASS.

- [ ] **Step 2: Run existing backend tests**

Run the repository's Python test suite from the project root.

Expected: PASS, including session, local-audio, wake-word, and sentinel coverage applicable to this branch.

- [ ] **Step 3: Verify forbidden regressions in source**

Confirm `backend/server.py` does not invoke local playback from `/api/tts`; confirm `/api/listen` and `/api/wake-listen` remain legacy-disabled on this branch; confirm `HomeShell` remains the owner of active session conversation.

- [ ] **Step 4: Manual acceptance test**

Start backend and frontend. Activate ORION normally. Ask for a long answer. While GEVER is speaking, say a new sentence without saying `ORION`. Expected: current audio stops quickly, the new sentence is captured once, GEVER answers it once, and the session stays active. Repeat once with background transient noise; expected: GEVER does not stop for the transient.

- [ ] **Step 5: Commit only if verification required a scoped fix**

If no fix was needed, do not create an empty commit.