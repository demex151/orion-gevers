# GEVER Autonomous Visual Manager — Design

Date: 2026-08-27

## Goal
Transform the GEVER home experience into an ambient AI interface rather than a traditional dashboard.

## Non-negotiable constraints
- Preserve the exact current GEVER sphere/orb visual.
- Preserve the exact current background.
- Do not modify ORION wake-word behavior.
- Do not modify microphone/listening behavior.
- Do not modify working barge-in/interruption behavior.
- Do not modify NVIDIA/LLM behavior.
- Do not modify Lead Hunter behavior.
- Do not modify memory/backend behavior.
- Preserve the existing `salir` conversation exit behavior.

## Base screen
The normal home screen contains the existing background and existing GEVER sphere as the permanent visual identity. Existing fixed dashboard cards, calendar, communications, growth metrics, agent cards, and similar persistent information are removed from the primary view.

The sphere remains the visual center of GEVER and can reflect existing runtime states through surrounding presentation without replacing the current sphere asset.

## Autonomous Visual Manager
A frontend-only Visual Manager controls contextual floating panels around the sphere. It never calls business tools itself and never owns conversation logic. It only renders structured visual state supplied by the UI/runtime integration layer.

GEVER may show zero to three panels simultaneously. The manager selects safe predefined layout slots instead of arbitrary pixel coordinates, giving GEVER an autonomous appearance while preventing overlap or visual chaos.

Supported panel lifecycle:
- open
- update
- minimize
- replace
- close
- close all

## Layout behavior
The sphere and background remain fixed. Context panels occupy available zones around the sphere. The manager prioritizes the most relevant active panel and can reduce secondary panels when a new visual explanation is needed.

Maximum simultaneous panels: 3.

Initial layout slots:
- upper/right contextual panel
- lower/left contextual panel
- lower/right contextual panel

On smaller displays the manager automatically reduces the number of visible panels and uses a safe stacked layout.

## Initial panel types
The architecture supports contextual panels such as:
- agenda/calendar
- leads/opportunities
- metrics/charts
- task/progress
- communication summary
- generic structured information

The first implementation should use presentation-safe/demo data or existing frontend state only. Connecting real calendar or external account data is a separate integration task.

## Interaction principle
Panels appear only when visual information improves the current conversation or task. They are not permanent navigation pages. GEVER can continue speaking while a panel is visible, and the user remains on the same ambient home screen.

Example future interaction:
1. User asks GEVER to review the agenda.
2. GEVER obtains agenda information through the appropriate tool/integration.
3. Visual Manager opens an agenda panel beside the sphere.
4. GEVER explains the agenda while it remains visible.
5. User asks about leads.
6. Visual Manager may minimize the agenda and open a leads panel in another safe slot.
7. Irrelevant panels close automatically as conversational context changes.

## Visual style
Panels should feel holographic/floating rather than like conventional application windows: restrained transparency, depth, subtle borders/glow, and short entrance/exit transitions. Effects must remain lightweight and must not replace or visually alter the existing sphere/background.

## Safety boundary
The visual redesign is frontend presentation work. Existing runtime functions remain authoritative for voice, wake word, AI responses, lead search, memory, and conversation termination. Visual Manager failures must not stop GEVER from speaking, listening, or executing existing tools.

## Verification
Before considering the redesign complete:
- existing barge-in tests remain green;
- existing speech playback tests remain green;
- existing global audio barge-in tests remain green;
- frontend builds successfully;
- Python test suite remains unchanged/passing;
- manual smoke test confirms ORION activation, conversation, interruption, Lead Hunter, and `salir` still work;
- sphere and background are visually unchanged.
