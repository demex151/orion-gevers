# Lead Hunter Live Telemetry Design

## Goal
When GEVER is asked to find painting opportunities, show the real Lead Hunter workflow in contextual floating graphics while the task runs, then return to the ambient background + sphere home.

## Non-negotiable behavior
- Telemetry must represent real Lead Hunter activity, never simulated progress.
- Existing evaluator decisions remain authoritative and unchanged.
- Existing ORION, microphone, barge-in, TTS, NVIDIA/brain behavior and `salir` remain unchanged.
- The permanent home remains only the existing background and existing sphere.
- Task panels exist only while useful and use the existing Visual Manager safe slots.

## Workflow represented
1. Search opportunities.
2. Analyze results.
3. Discard competitors.
4. Discard directories.
5. Discard advertising/provider marketing.
6. Discard contractors looking for work.
7. Discard stale publications.
8. Identify real buyer intent for painting.
9. Eliminate/merge duplicates.
10. Classify opportunities and persist results.

The evaluator may perform several rejection checks inside one evaluation call. Telemetry therefore reports the actual rejection reason returned by the evaluator and maps that reason into the appropriate visible category rather than pretending each candidate traversed ten separately timed functions.

## Backend telemetry
Add a small thread-safe in-memory telemetry broker. `LeadHunter.run()` accepts an optional progress callback and emits structured snapshots/events at run start, query/provider search, each finding evaluation, rejection, duplicate detection, accepted classification, persistence, error, and completion. The callback must be optional so current callers and tests continue to work.

Expose read-only progress through a backend endpoint suitable for short polling. The chat request can continue synchronously as it does now; the UI observes telemetry independently. Telemetry failure is swallowed at the reporting boundary and can never fail the hunt.

## Event/snapshot model
A snapshot contains run id, state, active stage, totals (found/analyzed/rejected/valid/duplicates/saved), rejection buckets (competition/directories/advertising/contractors/stale/other), classification buckets (HOT/WARM/PROSPECT), current query/provider, last evidence summary, timestamps, and completion/error state.

## Frontend visualization
The Visual Manager opens a Lead Hunter workspace only when a real hunt becomes active. Up to three contextual panels may appear around the centered sphere:
- Pipeline: the workflow stages with active/completed state.
- Live counters: found, analyzed, discarded, valid, duplicates, saved plus rejection distribution bars.
- Results: HOT/WARM/PROSPECT distribution and final summary.

Panels update from backend telemetry and close after a short completed-state presentation, returning to background + sphere. The sphere remains animated by its existing runtime state system.

## Failure isolation
If telemetry endpoint, polling, rendering, or a panel fails, the Lead Hunter still completes normally and voice response remains unaffected. No telemetry code may own microphone/audio state.

## Verification
Add Python tests for emitted real events, rejection mapping, duplicate/classification/persistence counts, callback failure isolation, and progress endpoint. Add frontend model/controller tests for snapshot-to-panel conversion, active stage progression, completion, and no-panel idle state. Re-run existing Lead Hunter, brain tool, listener, barge-in and speech playback regressions.
