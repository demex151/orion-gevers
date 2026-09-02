# GEVER 3D Dashboard — Approved Design

## Goal
Rebuild the primary GEVER dashboard to match the approved futuristic HUD reference as closely as practical while preserving all existing voice, chat, TTS, backend, memory, and agent behavior.

The central visual must be real-time 3D, not a static image or video.

## Approved architecture

```text
GEVER Dashboard
├── Sidebar
├── GreetingHeader
├── SystemMetrics
├── GeverCore3D
│   ├── EnergyCore
│   ├── HolographicRings
│   ├── OrbitLines
│   ├── ParticleField
│   └── CoreStateController
├── ActiveAgents
├── GesturePanel
├── CommandBar
└── SystemFooter
```

## Frontend component layout

```text
frontend/src/
├── components/
│  ├── dashboard/
│  │  ├── Sidebar.jsx
│  │  ├── GreetingHeader.jsx
│  │  ├── SystemMetrics.jsx
│  │  ├── ActiveAgents.jsx
│  │  ├── GesturePanel.jsx
│  │  ├── CommandBar.jsx
│  │  └── SystemFooter.jsx
│  └── core3d/
│     ├── GeverCore3D.jsx
│     ├── EnergyCore.jsx
│     ├── HolographicRings.jsx
│     ├── OrbitLines.jsx
│     ├── ParticleField.jsx
│     └── CoreStateController.js
├── HomeShell.jsx
├── geverVisualBridge.js
└── styles/
   └── gever-dashboard.css
```

## 3D stack

Add:
- `three`
- `@react-three/fiber`
- `@react-three/drei`

React Three Fiber owns the WebGL scene. Normal React/CSS owns the HUD panels and navigation.

## Core visual

Replace the current layered Figma orb images with a true WebGL scene containing:
- luminous energy sphere/core
- several independently rotating rings
- segmented holographic arcs
- orbital paths
- particles and energy dust
- glow/bloom-like visual treatment
- depth and perspective
- continuous low-motion idle animation
- responsive animation based on GEVER state

The core is the visual representation of GEVER, not decoration.

## State integration

Preserve the existing GEVER visual bridge and use it as the boundary between application behavior and rendering.

```text
Existing GEVER runtime
        ↓
geverVisualBridge
        ↓
CoreStateController
        ↓
GeverCore3D
```

Supported visual states:
- `idle`
- `listening`
- `thinking`
- `speaking`
- `working`
- `error`

Example behavior:
- idle: slow rotation and breathing glow
- listening: stronger pulse and outward audio-reactive rings
- thinking: faster orbital motion and denser particle activity
- speaking: rhythmic core/ring response synchronized with speech state
- working: directional orbit activity and stronger HUD indicators
- error: restrained warning-state animation without destroying scene continuity

## Existing behavior that must remain intact

Do not break or rewrite working backend functionality. Preserve:
- `/api/chat`
- `/api/tts`
- existing voice state/status integration
- existing navigation behavior where still required
- memory and agent functionality
- legacy application as a temporary fallback during migration

`HomeShell.jsx` currently owns command submission, TTS playback and status handling. Extract UI responsibilities gradually rather than deleting that behavior.

## Dashboard fidelity

The approved reference is the target layout, not merely inspiration. Reproduce:
- dark full-screen HUD
- cyan/blue holographic visual language
- left navigation rail
- system metrics panel
- dominant central 3D GEVER core
- right-side active-agent panel
- gesture status/control panel
- command input region
- compact system/status indicators
- thin luminous borders, grids, technical markings and depth cues

Avoid generic SaaS cards or a conventional admin-dashboard appearance.

## Gestures

The first architecture must be gesture-ready. Gesture recognition is isolated from Three.js through a controller/event layer so camera tracking can later send normalized commands such as:
- rotate
- zoom
- select
- open panel
- close panel
- reset view

Camera/hand-tracking code must not directly mutate Three.js objects.

## Performance

- Keep the HUD usable if WebGL is temporarily unavailable.
- Limit particle counts according to device capability.
- Avoid unnecessary React re-renders in the animation loop.
- Use `useFrame`/refs for continuous scene animation.
- Keep system/agent panels as normal DOM elements rather than rendering all UI into WebGL.

## Migration strategy

1. Add 3D dependencies and core-state mapping with tests.
2. Build `GeverCore3D` in isolation.
3. Replace the Figma-image orb while preserving the existing dashboard shell.
4. Extract dashboard panels from `HomeShell.jsx` into dedicated components.
5. Match the approved reference layout and responsive behavior.
6. Connect real GEVER state to the 3D scene.
7. Add gesture-controller boundary and visual gesture panel.
8. Add real camera hand tracking as a separate integration phase.
9. Run frontend tests/build and backend regression tests before merge.

## Non-goals

- Do not redesign the backend.
- Do not replace NVIDIA/GEVER AI behavior.
- Do not remove legacy functionality until the new dashboard is verified.
- Do not substitute a prerendered image/video for the 3D core.

## Acceptance criteria

The dashboard should visually read as the approved GEVER HUD immediately on load. The central object must have genuine perspective and independent 3D motion. Existing chat/TTS actions must still work. Visual state changes must affect the core without coupling backend code to Three.js. The implementation must build cleanly and preserve existing tests before it is considered ready to merge.