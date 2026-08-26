# GEVER Lead Hunter Production Design

## Purpose

GEVER Lead Hunter is the first production-work subsystem for GEVER. Its job is to discover real, public, organic business opportunities for a painting company, evaluate them, remove duplicates, classify them, store them locally, and present them for human approval before any outreach occurs.

The first version is PC-first and runs entirely from the user's computer. It must work with live public Internet data from the beginning rather than laboratory-only test data.

## Core Principles

- Use only public, organically available information.
- Do not purchase lead databases or paid prospect data.
- Do not contact, message, post, or otherwise reach out to anyone without explicit user approval.
- Keep the existing GEVER voice, wake-word, session, memory, and TTS systems isolated from Lead Hunter implementation.
- Store leads locally on the PC in the first version.
- Support both manual searches and automatic searches every 2 hours while GEVER is running.
- Design components so social-media monitoring and automated follow-up can be added later without rewriting the core.

## User Experience

The user can manually trigger Lead Hunter with a command such as:

`GEVER, busca nuevos clientes.`

GEVER launches a production search, finds and analyzes opportunities, then displays results in the Lead Hunter dashboard.

The scheduler also launches Lead Hunter automatically every 2 hours while GEVER is running.

HOT + URGENT opportunities are highlighted visually in the dashboard. They do not interrupt the user by voice.

## Search Territory

Initial coverage is Myrtle Beach and nearby serviceable areas, including:

- Myrtle Beach
- North Myrtle Beach
- Conway
- Carolina Forest
- Socastee
- Surfside Beach
- Garden City
- Murrells Inlet
- Little River
- Other nearby areas that are reasonably serviceable from the same market

The territory must be configuration-driven so it can be expanded later without changing search-engine code.

## Opportunity Types

Lead Hunter runs two discovery strategies in parallel.

### Active Demand Hunter

Finds public evidence that a person or business is currently requesting a service that the painting company can perform.

Examples include public requests for:

- interior painting
- exterior painting
- cabinet painting
- drywall-related work
- pressure washing
- compatible repair/preparation work

Active demand receives higher intent weighting because the need is explicit.

### Prospect Hunter

Finds public signals that indicate a reasonable business opportunity even when no explicit painting request has been published.

Examples include:

- property managers
- Realtors
- HOAs
- rental properties
- recently renovated or maintained properties
- businesses with maintenance or repainting signals
- other public commercial or property signals with a plausible need for painting services

Prospecting must be evidence-based. GEVER must not invent a need merely because an entity exists.

## Research Architecture

### Lead Hunter Orchestrator

Coordinates a complete search run.

Responsibilities:

- receive manual or scheduled search requests
- generate search tasks for active demand and prospecting
- invoke the Web Research Engine
- pass findings through validation, deduplication, scoring, and storage
- produce a run summary for the dashboard

The orchestrator must not scrape social networks through unofficial private APIs or bypass access controls.

### Web Research Engine

The research engine performs public Internet discovery through a hybrid approach:

- general web search strategies
- source-specific adapters added over time for public sources that consistently produce useful leads

Each raw finding must preserve:

- source URL
- source name/domain
- title or public identifier
- public excerpt/evidence
- discovery timestamp
- publication timestamp when available
- location clues
- contact clues when publicly exposed

The research engine must distinguish direct evidence from inferred metadata.

## Validation

### Lead Validator

Rejects or downgrades findings that are not actionable opportunities.

It must check for:

- service-area relevance
- service compatibility
- freshness/recency
- evidence that the item represents a customer/prospect rather than another contractor
- job-seeker or employment-posting false positives
- stale directories with no current intent
- irrelevant pages, generic SEO pages, or content with no opportunity signal

A rejected finding should preserve a reason in run diagnostics but should not enter the active lead queue.

## Deduplication

### Deduplicator

The same opportunity may appear through multiple searches or URLs. Lead Hunter must consolidate likely duplicates before presenting them.

Deduplication may use normalized combinations of:

- canonical/source URL
- normalized name or company
- location/address clues
- public contact data
- source identifiers
- normalized evidence text

A lead keeps one persistent `lead_id`. New evidence can be appended to the same lead rather than creating a duplicate.

## Classification Model

Intent and readiness are separate concepts.

### HOT

A lead is HOT only when it is ready for practical action. It should have:

- a clear current or strongly supported need
- a compatible service
- a serviceable location
- source/evidence that can be verified
- enough public information to contact or respond through the original public channel

HOT does not merely mean urgent.

### WARM

A real or strongly supported opportunity exists, but one or more important details are missing or intent is less immediate.

### PROSPECT

No explicit request has been made, but public evidence suggests a reasonable opportunity worth reviewing.

### URGENT

`URGENT` is an independent boolean/priority flag. It indicates time sensitivity rather than completeness.

Example:

A public post saying `Need a painter this week in Conway` may be WARM + URGENT if contact information is incomplete. It becomes HOT + URGENT when enough information exists to act.

## Lead Score

The internal score is used for ordering and diagnostics, not as a substitute for category rules.

Suggested weighted factors:

- explicit service need
- recency
- geographic fit
- service fit
- evidence quality
- available contact/reply path
- urgency
- confidence that the result is a buyer/prospect rather than noise

The score and the category must both be stored so GEVER can explain why a lead ranks highly.

## Lead Data Model

Each lead has one persistent `lead_id` and at minimum stores:

- `lead_id`
- `classification`: `HOT | WARM | PROSPECT`
- `urgent`: boolean
- `score`
- `status`
- `name`
- `organization`
- `location`
- `service_requested_or_inferred`
- `opportunity_type`: `ACTIVE_DEMAND | PROSPECT`
- `source_url`
- `source_domain`
- `source_title`
- `evidence`
- `published_at` when available
- `discovered_at`
- `public_contact_method` when available
- `missing_information`
- `recommended_action`
- `validation_notes`
- `first_seen_at`
- `last_seen_at`
- `evidence_history`

Unknown fields remain null/empty; GEVER must not invent them.

## Commercial Workflow Status

The lead workflow uses these states:

- `NEW`
- `REVIEWED`
- `APPROVED`
- `CONTACTED`
- `FOLLOW_UP`
- `WON`
- `LOST`

Classification and workflow status are independent. For example, a HOT lead can be `NEW`, `APPROVED`, or `CONTACTED`.

## Local Storage

The first production version is local-first and PC-only.

Use a local database suitable for transactional lead storage and querying. SQLite is preferred unless an existing project database makes another local option clearly simpler.

Lead Hunter storage is separate from conversational memory. Business leads must not be stored as ordinary GEVER memory records.

The database must preserve:

- leads
- evidence history
- search runs
- rejected findings with diagnostic reason
- workflow state changes
- timestamps needed for deduplication and reporting

Cloud synchronization and phone access are explicitly deferred.

## Dashboard

Lead Hunter gets a production dashboard in GEVER's existing frontend.

The dashboard must provide:

- HOT + URGENT highlighted first
- HOT
- WARM
- PROSPECT
- source and evidence visibility
- location and service
- discovered/published time
- public contact/reply method when available
- missing information
- recommended action
- workflow status
- actions to approve, discard/mark lost, mark contacted, and set follow-up

A lead's source/evidence must be inspectable so the user can verify GEVER's judgment.

## Scheduling

Lead Hunter supports:

### Manual mode

Triggered by user command/API/UI and runs immediately.

### Automatic mode

Runs every 2 hours while the GEVER backend is running.

The scheduler must prevent overlapping runs. If a scheduled run is due while another Lead Hunter run is still active, it should skip or defer rather than start a duplicate concurrent run.

## GEVER Integration

GEVER's existing conversational brain remains intact.

A thin task-routing layer may identify explicit Lead Hunter commands and invoke the Lead Hunter service. The production subsystem should expose a clear service/API boundary rather than putting web-research logic directly inside `GeversBrain.think()`.

The existing voice flow is only a trigger/interface. Lead Hunter remains independently testable without microphone or TTS.

## Safety and Human Approval Boundary

Lead Hunter may automatically:

- search public Internet sources
- open/read public pages where technically and legally accessible
- analyze results
- score/classify leads
- store/update leads
- recommend actions
- schedule additional organic searches

Lead Hunter may not automatically:

- send email
- send direct messages
- post comments
- submit forms
- call people
- publish social content
- impersonate the user
- bypass login/access controls
- evade anti-bot restrictions

Any future outreach module must have its own approval and design.

## Observability

Every search run must record enough information to diagnose quality:

- run ID
- start/end time
- manual or scheduled trigger
- search strategies/queries issued
- source domains seen
- raw findings count
- accepted leads count
- rejected findings count
- duplicate merges count
- HOT/WARM/PROSPECT counts
- errors by source/adapter

This allows GEVER to learn operationally which public strategies produce useful opportunities without treating unverified Internet content as permanent conversational memory.

## Failure Behavior

Lead Hunter must fail independently from the normal GEVER conversation system.

If Internet research fails:

- voice/chat remain operational
- the current run records an error
- previously stored leads remain accessible
- automatic scheduling continues with later runs

If one source fails, other search strategies should continue when possible.

## Deferred Capabilities

Not part of this first implementation:

- Facebook/Instagram account automation
- monitoring comments/messages on owned social posts
- automatic outreach
- automatic follow-up messages
- cloud synchronization
- phone access
- paid lead/data providers
- autonomous estimates or contracts

These are intended future modules and must connect through the lead database and task interfaces instead of rewriting Lead Hunter.

## Acceptance Criteria

The first production version is successful when:

1. A user can trigger a live Lead Hunter search from GEVER on the PC.
2. GEVER searches public Internet sources using both active-demand and prospect strategies.
3. Findings are validated and irrelevant results are rejected.
4. Duplicate opportunities are consolidated.
5. Accepted leads are stored locally with source/evidence.
6. Leads receive HOT/WARM/PROSPECT classification plus independent URGENT flag.
7. The dashboard displays prioritized leads and allows workflow-state changes.
8. Automatic searches run every 2 hours without overlapping runs.
9. No outreach occurs without user approval.
10. Lead Hunter failures do not break GEVER voice/chat functionality.