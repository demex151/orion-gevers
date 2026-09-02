const PROFILES = {
  idle: { state: "idle", rotationSpeed: 0.08, pulse: 0.025, particleEnergy: 0.25, orbitSpeed: 0.12, scale: 1 },
  listening: { state: "listening", rotationSpeed: 0.13, pulse: 0.055, particleEnergy: 0.45, orbitSpeed: 0.18, scale: 1.02 },
  thinking: { state: "thinking", rotationSpeed: 0.24, pulse: 0.07, particleEnergy: 0.72, orbitSpeed: 0.34, scale: 1.03 },
  speaking: { state: "speaking", rotationSpeed: 0.18, pulse: 0.12, particleEnergy: 0.58, orbitSpeed: 0.24, scale: 1.04 },
  working: { state: "working", rotationSpeed: 0.28, pulse: 0.085, particleEnergy: 0.82, orbitSpeed: 0.4, scale: 1.05 },
  error: { state: "error", rotationSpeed: 0.06, pulse: 0.09, particleEnergy: 0.35, orbitSpeed: 0.08, scale: 0.98 },
};

export function getCoreMotionProfile(coreState = "idle") {
  return PROFILES[coreState] ?? PROFILES.idle;
}
