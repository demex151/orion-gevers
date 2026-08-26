# GEVER Sentinel Audio — Design

## Goal

Replace GEVER's current always-transcribing idle loop with a local sentinel mode. When a conversation ends, normal speech recognition must stop. GEVER remains locally wakeable by either a double clap or the wake word ORION, without sending idle audio to the brain or chat pipeline.

## Scope

This phase changes only activation and session lifecycle. It does not replace GEVER's brain, memory, Figma UI, agent runtime, or chat model. OpenJarvis-style orchestration is a later phase after the audio/session foundation is stable.

## Required behavior

GEVER has three explicit states:

- `SENTINEL`: no conversational transcription. A lightweight local audio monitor is allowed to inspect short audio frames only for activation signals.
- `SESSION`: normal speech recognition is active and user speech can be sent to GEVER's chat endpoint.
- `STOPPED`: all audio capture is stopped, used for application shutdown or an explicit full-stop control.

On application startup GEVER enters `SENTINEL`.

From `SENTINEL`, either a valid double clap or local detection of `ORION` opens `SESSION`.

From `SESSION`, natural close commands such as `cierra la sesión`, `cerremos la sesión`, `cierra el chat`, `terminemos`, `hasta aquí`, `deja de escuchar`, and the UI Finalizar control close the session. Closing a session must cancel normal conversational listening before returning to `SENTINEL`.

Returning to `SENTINEL` must not call the existing `/api/listen` conversational recognizer until a new activation occurs.

## Components

### SentinelMonitor

A new backend audio component with one responsibility: detect activation while GEVER is idle.

It owns the low-level input stream while in sentinel mode and exposes activation events. It must not call the brain, memory, `/api/chat`, or TTS.

The double-clap detector is adapted from the useful pattern in `hectorg2211/jarvis`: short audio frames, RMS/energy measurement, adaptive ambient noise floor, spike ratio, minimum/maximum spacing between claps, reset/cooldown, and a requirement that energy fall between peaks. Thresholds are configurable rather than hardcoded into the UI.

### Local ORION detector

ORION must be detected locally in sentinel mode. It must not use GEVER's conversational `/api/listen` loop. The detector is behind a small interface so the implementation can be changed without changing the session controller.

If the selected local wake-word implementation is unavailable on a machine, double clap remains operational and status reports ORION local wake as unavailable rather than silently falling back to continuous transcription.

### SessionController

A single controller owns transitions between `SENTINEL`, `SESSION`, and `STOPPED`. This eliminates competing microphone loops.

Only one audio owner may be active at a time:

1. Sentinel owns the microphone in `SENTINEL`.
2. Sentinel releases it before entering `SESSION`.
3. Conversational recognition owns it in `SESSION`.
4. Conversational recognition is cancelled/released before returning to `SENTINEL`.
5. Both are released in `STOPPED`.

### Frontend

The existing Figma design remains intact. The frontend receives state from the controller instead of inferring it from overlapping loops.

A `FINALIZAR CONVERSACIÓN` action is exposed only while a session is active. It invokes the same close-session transition used by spoken close commands. It does not merely change visual state.

## Data flow

Idle:

`microphone -> SentinelMonitor -> [double clap | local ORION] -> SessionController.open_session()`

Conversation:

`microphone -> speech recognition -> GEVER brain -> response -> TTS/UI`

Close:

`voice close command OR Finalizar -> cancel conversational listen -> release microphone -> SessionController.close_session() -> SentinelMonitor`

No chat request is produced from idle sentinel audio.

## Voice

Voice replacement is intentionally separated from sentinel/session work. The first milestone preserves the currently working TTS path so activation regressions can be isolated. After session lifecycle tests pass on the user's Windows machine, the voice provider can be replaced independently.

The exact voice used by another Jarvis project will not be claimed or copied unless its provider/voice identifier or a legitimately usable voice asset is available. Voice style and provider are separate from the sentinel architecture.

## Failure handling

- Microphone unavailable: controller reports `audio_unavailable`; no retry storm.
- Sentinel stream fails: close stream cleanly, report error, allow manual UI activation.
- ORION detector unavailable: keep double clap active and expose degraded status.
- Conversational listen hangs during close: cancellation has a bounded timeout; controller does not start sentinel until conversational audio ownership is released.
- TTS/chat failure during a session does not implicitly close the session.
- Application shutdown transitions to `STOPPED` and releases all audio resources.

## Configuration

Audio activation configuration lives outside UI code. Initial settings include:

- sentinel enabled
- double-clap enabled
- ORION local wake enabled
- input device override
- clap sensitivity/spike ratio
- clap minimum and maximum gap
- clap cooldown

Safe defaults are provided; advanced tuning can be added later.

## Testing

Unit tests cover:

- legal state transitions
- no simultaneous sentinel/conversation audio ownership
- double-clap timing and reset behavior
- false single-clap rejection
- close-command normalization and matching
- closing a session cancels conversational listening before sentinel restart
- ORION detector failure degrades to clap-only mode

Integration tests use fake audio/wake adapters so CI does not require a physical microphone.

Manual Windows acceptance test:

1. Start GEVER: status is sentinel, no conversational transcription requests loop.
2. Speak ordinary words without ORION: no chat/transcription response.
3. Double clap: session opens once.
4. Close the session by voice: conversational listening stops and sentinel resumes.
5. Double clap again: a new session opens.
6. Close with the UI button: same transition occurs.
7. Say ORION while sentinel is active: session opens if the local wake engine is available.
8. Confirm only one process owns GEVER's audio capture path at each transition.

## Implementation boundaries

Do not integrate OpenJarvis orchestration, new agents, browser automation, or unrelated UI redesign in this phase. Do not rewrite GEVER's brain. Do not run sentinel and conversational recognition concurrently.

The next implementation plan will break this into independently testable commits, with the current working branch retained as the rollback point.