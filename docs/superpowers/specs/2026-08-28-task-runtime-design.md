# GEVER Task Runtime Design

## Goal
Introduce a modular capability/task execution architecture inspired by jarvis-demo's primitive/builder separation while preserving GEVER's existing voice, NVIDIA, memory, Lead Hunter, visual panels, and stored-result behavior.

## Architecture
`GeversBrain` remains the conversational entry point. Task-like commands are delegated to a `TaskRouter`, which resolves a registered `Capability`. `TaskRuntime` executes that capability and records a common `TaskOutcome`. Capabilities own execution and verification. Lead Hunter is the first migrated capability and continues using the existing hunter, store, and telemetry.

Flow: `Voice/API -> GeversBrain -> TaskRouter -> TaskRegistry -> TaskRuntime -> Capability -> Verifier -> TaskOutcome`.

## Compatibility constraints
- Do not change ORION wake/listen behavior.
- Do not change TTS, microphone, barge-in, NVIDIA configuration, or memory behavior.
- Preserve all existing Spanish Lead Hunter commands and response wording.
- Preserve existing Lead Hunter telemetry so the current Visual Manager continues working.
- Preserve stored-result and graph-display commands.
- Conversation that does not match a capability continues through NVIDIA exactly as before.

## Core contracts
A capability exposes `name`, `signals`, `matches(text)`, `execute(context)`, and `verify(result)`. The registry owns registered capabilities and deterministic resolution. The router returns a capability or `None`. The runtime owns task lifecycle states: `started`, `running`, `verifying`, `completed`, `failed`.

`TaskOutcome` contains `task_id`, `capability`, `status`, `started_at`, `finished_at`, `result`, `error`, and `verified`.

## Lead Hunter migration
The existing Lead Hunter implementation remains unchanged. A `LeadHunterCapability` receives callbacks for obtaining the hunter and store, executes `hunter.run(trigger="voice", progress_callback=lead_hunter_telemetry.publish)`, verifies that a summary object contains the expected counts, and formats the exact current Spanish response. `GeversBrain._run_lead_hunter()` becomes a compatibility wrapper around the runtime so existing tests/callers remain valid.

## Failure containment
Capability exceptions are caught by `TaskRuntime` and represented as failed outcomes. They must not corrupt the registry or conversational history. The brain converts a failed outcome into a concise Spanish error rather than claiming completion.

## Extensibility
Future capabilities such as calendar, social, content, image/flyer, and website workers register without adding execution logic to `brain.py`. Later phases may move selected workers to separate OS processes while retaining these contracts.

## Testing
Add focused tests for registry resolution, router conversation fallback, runtime lifecycle/success/failure/verification, and Lead Hunter capability compatibility. Run the complete existing Python suite after migration. Frontend files are not modified in this phase.