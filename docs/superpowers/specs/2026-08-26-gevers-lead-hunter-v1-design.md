# Gevers Lead Hunter V1 Design

## Goal
Build the first real Lead Hunter for Gevers Painting: discover public painting opportunities in Myrtle Beach and Horry County, turn findings into structured lead candidates, reject low-quality findings, score and classify useful opportunities, deduplicate them, and persist them for human review.

## Scope
V1 is exclusively for Gevers Painting and its local service area. It does not contact prospects automatically. It only discovers, evaluates, prioritizes, and stores public opportunities.

## Existing foundation
The branch already provides LeadCandidate/LeadRecord models, HOT/WARM/PROSPECT classification, ACTIVE_DEMAND/PROSPECT opportunity types, lifecycle statuses, SQLite persistence, evidence history, deduplication, run summaries, and rejection recording.

## Architecture
The discovery pipeline is split into focused units:

1. `GeversLeadProfile`: fixed V1 business/service-area rules for Gevers Painting.
2. `SearchProvider`: provider interface returning normalized public search findings. V1 includes a web-search HTTP provider boundary so providers can be replaced without changing classification or storage.
3. `LeadEvaluator`: deterministic first-pass validation and scoring. It checks local geography, painting/service intent, active-demand language, evidence quality, and obvious irrelevant content.
4. `LeadHunter`: orchestration. It starts a search run, asks providers for findings, evaluates each finding, records rejected findings, upserts accepted candidates into LeadStore, updates counters, and finishes the run even when one provider fails.
5. CLI entry point: a manual command to run a hunt and print a compact summary and prioritized leads.

## Search strategy
Queries target painting demand and property-improvement intent around Myrtle Beach/Horry County, including interior painting, exterior painting, cabinet painting/refinishing, drywall/paint repair, commercial painting, and requests for painter/painting contractor/quotes/estimates.

Search access is isolated behind the provider interface. The core must not scrape arbitrary sites directly or depend on private/authenticated content. Only publicly accessible result metadata/evidence is accepted.

## Evaluation rules
A finding must contain a public URL and meaningful textual evidence. Findings outside the configured service area or unrelated to supported painting services are rejected.

Strong explicit demand such as asking for a painter, quote, estimate, recommendation, availability, or a painting job is `ACTIVE_DEMAND`. Business/property records that indicate a plausible target but no explicit current request are `PROSPECT` and rank below active demand.

Scores are deterministic on a 0-100 scale. Geography, explicit painting intent, urgency/recency language, and usable public contact evidence add points. Weak/ambiguous evidence reduces confidence. Classification thresholds are HOT >= 75, WARM >= 50, otherwise PROSPECT, with explicit active demand required for HOT.

Deduplication uses normalized source URL plus normalized identity/evidence information so repeated discovery updates the existing lead and evidence history instead of creating a new lead.

## Failure handling
A provider failure is recorded in the search-run `errors` map and does not discard successful findings from other providers. Individual malformed/irrelevant findings are recorded as rejections with a reason. A run always receives an end timestamp.

## Safety and review boundary
Lead Hunter V1 never sends messages, calls, posts, submits forms, or purchases lead data. Every discovered opportunity remains NEW until reviewed by the user.

## Testing
Unit tests cover geography filtering, painting-intent filtering, active-demand classification, score thresholds, deterministic dedupe keys, provider failure isolation, rejection recording, persistence, and run counters. Existing repository tests must continue to pass.

## Success criteria
A manual hunt can consume public search findings, persist only relevant local painting opportunities, rank HOT before WARM before PROSPECT, merge duplicates, expose evidence/source URLs, and complete without breaking the existing test suite.
