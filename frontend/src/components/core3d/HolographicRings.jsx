import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { getCoreMotionProfile } from "./CoreStateController.js";

const RINGS = [
  { radius: 1.18, tube: 0.018, rotation: [1.18, 0.1, 0.18], speed: 1.15, opacity: 0.72, color: "#7bf7ff" },
  { radius: 1.42, tube: 0.013, rotation: [0.42, 0.62, 1.05], speed: -0.82, opacity: 0.62, color: "#43baff" },
  { radius: 1.72, tube: 0.011, rotation: [1.45, 0.18, 0.72], speed: 0.64, opacity: 0.54, color: "#64f2ff" },
  { radius: 1.98, tube: 0.009, rotation: [0.82, 1.1, 0.25], speed: -0.48, opacity: 0.46, color: "#2f8cff" },
  { radius: 2.23, tube: 0.007, rotation: [1.24, 0.48, 1.32], speed: 0.36, opacity: 0.36, color: "#67e8ff" },
  { radius: 2.48, tube: 0.005, rotation: [0.58, 1.4, 0.82], speed: -0.24, opacity: 0.28, color: "#397dff" },
];

const NODES = [
  [2.48, 0, 0],
  [-2.14, 1.06, 0.2],
  [1.82, -1.48, -0.15],
  [-1.35, -1.84, 0.45],
];

export default function HolographicRings({ coreState = "idle" }) {
  const refs = useRef([]);
  const nodesRef = useRef(null);
  const profile = getCoreMotionProfile(coreState);

  useFrame((_, delta) => {
    refs.current.forEach((ring, index) => {
      if (!ring) return;
      ring.rotation.z += delta * profile.orbitSpeed * RINGS[index].speed;
      ring.rotation.y += delta * profile.rotationSpeed * 0.25 * RINGS[index].speed;
    });
    if (nodesRef.current) nodesRef.current.rotation.z -= delta * profile.orbitSpeed * 0.22;
  });

  return (
    <group>
      {RINGS.map((ring, index) => (
        <mesh key={ring.radius} ref={(node) => { refs.current[index] = node; }} rotation={ring.rotation}>
          <torusGeometry args={[ring.radius, ring.tube, 8, 160]} />
          <meshBasicMaterial color={ring.color} transparent opacity={ring.opacity} depthWrite={false} />
        </mesh>
      ))}

      <group ref={nodesRef} rotation={[0.9, 0.35, 0.2]}>
        {NODES.map((position, index) => (
          <group key={index} position={position}>
            <mesh>
              <sphereGeometry args={[0.045, 14, 14]} />
              <meshBasicMaterial color={index % 2 ? "#4f9fff" : "#8dfaff"} transparent opacity={0.95} />
            </mesh>
            <pointLight color="#5feaff" intensity={0.8} distance={0.8} />
          </group>
        ))}
      </group>
    </group>
  );
}
