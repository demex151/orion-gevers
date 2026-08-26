# GEVER Barge-In Voice Interruption Design

## Goal

Allow the user to interrupt GEVER naturally while GEVER is speaking. Any real user speech during TTS playback should stop the current browser audio immediately, capture the user's new utterance, and continue through the existing conversation flow.

## Non-goals

This change must not alter the existing wake-word behavior, session state machine, `/api/chat`, `/api/tts` response generation, memory behavior, or the current single browser audio playback path. It must not restore local Windows Media Player playback. It must not enable the hidden legacy React controller to own the microphone.

## Current Flow

During an active `SESSION`, `HomeShell.jsx` performs this sequence:

1. `sessionClient.listen()` captures the user's utterance.
2. The frontend sends the utterance to `/api/chat`.
3. The frontend sends the answer to `/api/tts`.
4. The returned audio blob is played in the browser.
5. After playback ends, the conversation loop returns to `sessionClient.listen()`.

The microphone is therefore not actively capturing the user while GEVER is speaking.

## Desired Flow

During an active `SESSION`:

1. GEVER begins browser TTS playback.
2. A dedicated barge-in detector starts monitoring microphone input only for the duration of GEVER's playback.
3. If no user speech is detected, playback completes normally and the existing conversation loop resumes unchanged.
4. If real user speech is detected:
   - stop the current browser audio immediately;
   - mark the current TTS as interrupted;
   - retain the utterance that caused the interruption;
   - feed that utterance into the same `/api/chat` path used by a normal conversation turn;
   - generate and play the new response;
   - keep the session active.

The user does not need to say `ORION` to interrupt during an already active session.

## Architecture

### `bargeInController`

Add a small, isolated frontend module responsible only for interruption detection while TTS is active. It should expose a narrow interface such as:

- `start({ onSpeech })`
- `stop()`

The controller must not own session state, chat requests, TTS generation, or wake-word activation.

### Browser Audio Playback

The current audio playback helper must expose a cancellable playback handle so `HomeShell` can stop the active `Audio` element immediately. The existing playback behavior remains unchanged when no interruption occurs.

### HomeShell Integration

`HomeShell.jsx` remains the single owner of the active conversation loop. While `speak(answer)` is running, it starts the barge-in detector. If the detector fires, `HomeShell` stops playback and carries the captured utterance forward as the next conversation turn instead of calling a second independent listen loop.

This avoids introducing two simultaneous conversation controllers.

## Speech Detection and Echo Protection

A simple volume threshold is not sufficient because GEVER's own speaker output could trigger the interruption. The detector should use browser microphone capture with speech-oriented constraints where available:

- `echoCancellation: true`
- `noiseSuppression: true`
- `autoGainControl: true`

The detector should require sustained voice-like activity for a short confirmation window before firing. A single click, keyboard tap, clap, or brief transient should not interrupt GEVER.

The initial implementation should favor conservative interruption detection over aggressive sensitivity. False interruptions from GEVER's own voice are considered a failure.

## State and Concurrency Rules

Only one of these operations may own a normal conversation turn at a time:

- regular `sessionClient.listen()`
- barge-in capture while TTS is playing

The barge-in detector is active only while browser audio is playing and only when the session state is `SESSION`.

When barge-in succeeds:

- the current playback is cancelled exactly once;
- the normal conversation loop must not open another microphone capture for the same utterance;
- the captured utterance becomes the next turn directly;
- the interrupted answer is not replayed or resumed.

When the session closes or the component unmounts, all barge-in microphone streams, timers, audio contexts, and event listeners must be released.

## Error Handling

If microphone permission for barge-in is unavailable, GEVER must continue working exactly as it does today: finish speaking, then listen normally. Barge-in failure must degrade gracefully rather than break the conversation.

If the detector encounters an internal error during playback, log the error, stop the detector, and allow the current TTS to finish normally.

If browser audio is cancelled because of a confirmed interruption, that cancellation is expected behavior and must not be surfaced as a connection error.

## Testing

Add focused tests for the interruption controller and integration behavior:

- no detected speech lets audio finish normally;
- confirmed user speech stops active playback once;
- a transient noise does not stop playback;
- an interrupted utterance is processed as the next chat turn exactly once;
- session close cleans up detector resources;
- detector failure falls back to the existing non-interruptible behavior;
- legacy microphone endpoints remain disabled;
- no Windows local playback is reintroduced.

## Acceptance Criteria

The feature is complete when, during an active conversation, GEVER can be speaking a long answer and the user can begin speaking naturally without saying `ORION`; GEVER stops speaking quickly, captures the user's new statement, responds to it once, and remains in the same conversation session. Existing wake-word activation, normal listening, chat, TTS, memory, and browser-only playback continue to behave as before.