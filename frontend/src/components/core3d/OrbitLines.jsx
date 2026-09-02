import { Line } from "@react-three/drei";

const ORBITS = [
  { scale: [2.6, 1.05, 2.6], rotation: [Math.PI / 2.4, 0.25, 0.1], color: "#38d8ff" },
  { scale: [2.9, 1.2, 2.9], rotation: [Math.PI / 3.2, 1.05, 0.65], color: "#7a8cff" },
  { scale: [3.25, 1.38, 3.25], rotation: [Math.PI / 1.8, 0.45, 1.1], color: "#2fa9ff" },
];

function ellipsePoints(segments = 96) {
  return Array.from({ length: segments + 1 }, (_, index) => {
    const angle = (index / segments) * Math.PI * 2;
    return [Math.cos(angle), 0, Math.sin(angle)];
  });
}

const POINTS = ellipsePoints();

export default function OrbitLines() {
  return (
    <group>
      {ORBITS.map((orbit, index) => (
        <group key={orbit.color + index} rotation={orbit.rotation} scale={orbit.scale}>
          <Line points={POINTS} color={orbit.color} lineWidth={0.55} transparent opacity={0.24} />
        </group>
      ))}
    </group>
  );
}
