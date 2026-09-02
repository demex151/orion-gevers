import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { getCoreMotionProfile } from "./CoreStateController.js";

const RINGS = [
  { radius: 1.45, tube: 0.018, rotation: [1.08, 0.1, 0.18], speed: 1 },
  { radius: 1.78, tube: 0.012, rotation: [0.42, 0.62, 1.05], speed: -0.72 },
  { radius: 2.05, tube: 0.009, rotation: [1.45, 0.18, 0.72], speed: 0.48 },
  { radius: 2.32, tube: 0.006, rotation: [0.82, 1.1, 0.25], speed: -0.31 },
];

export default function HolographicRings({ coreState = "idle" }) {
  const refs = useRef([]);
  const profile = getCoreMotionProfile(coreState);

  useFrame((_, delta) => {
    refs.current.forEach((ring, index) => {
      if (!ring) return;
      ring.rotation.z += delta * profile.orbitSpeed * RINGS[index].speed;
      ring.rotation.y += delta * profile.rotationSpeed * 0.25 * RINGS[index].speed;
    });
  });

  return (
    <group>
      {RINGS.map((ring, index) => (
        <mesh key={ring.radius} ref={(node) => { refs.current[index] = node; }} rotation={ring.rotation}>
          <torusGeometry args={[ring.radius, ring.tube, 8, 128]} />
          <meshBasicMaterial color={index % 2 ? "#3da9ff" : "#62f5ff"} transparent opacity={0.58 - index * 0.08} depthWrite={false} />
        </mesh>
      ))}
    </group>
  );
}
