# GEVER Home Redesign Design

## Scope
Redesign only the `Inicio` screen of GEVER to closely match the user-provided futuristic reference images. Other pages remain visually and functionally unchanged for now.

## Visual direction
- Dark, premium, futuristic command-center aesthetic.
- Persistent left sidebar and structured top header.
- Cyan/blue primary illumination with restrained violet accents.
- Deep near-black layered background, subtle grids/glows, thin luminous borders, glass-like panels and controlled shadows.
- Central GEVER core as the dominant focal point, with concentric animated rings/orbits and state-reactive presentation.
- Right-side operational/status panel and lower information cards arranged to mirror the hierarchy and proportions of the reference Home screen.
- Typography, spacing, radii, borders and density should be consistent across the entire Home viewport and responsive on smaller desktop widths.

## Functional constraints
- Preserve the existing backend API contract at `http://127.0.0.1:8000`.
- Preserve ORION wake-word behavior and the current controller loop.
- Preserve manual talk, chat, TTS/audio playback, subtitles, conversation state and memory behavior.
- Do not change backend voice, brain, memory or server logic as part of this redesign.
- Do not redesign Memoria, Agentes, Analítica, Calendario or other navigation destinations in this phase.
- Avoid permanent fabricated business/system metrics. Static visual placeholders, when needed to reproduce the reference composition, must be isolated so they can later be replaced with real data.

## Frontend architecture
Keep the current React application and existing behavior in `frontend/src/App.jsx`. The Home markup may be reorganized into clearer visual sections, but behavior-critical functions and refs remain intact. `frontend/src/App.css` will receive the primary visual rewrite for the Home experience, using scoped classes so existing secondary pages are not unintentionally restyled.

## Interaction states
The GEVER core and status labels must visibly distinguish waiting, listening, thinking, preparing voice and speaking states. The existing talk control remains usable. Existing conversation and subtitle feedback remain available without requiring backend changes.

## Error handling
Existing API and voice errors continue to use the current application behavior. The redesign must not hide errors or make the interface unusable if TTS/chat/wake requests fail.

## Validation
- Frontend must build successfully with the existing Vite configuration.
- Existing Home controls must still invoke their current handlers.
- ORION/wake, manual talk, chat response, TTS and subtitles must retain their current frontend wiring.
- Navigation to existing pages must remain possible.
- Visual review should compare the Home screen against the supplied reference for hierarchy, proportions, lighting, panel treatment and overall density.
