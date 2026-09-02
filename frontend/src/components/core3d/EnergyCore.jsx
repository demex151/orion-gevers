import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { getCoreMotionProfile } from "./CoreStateController.js";

const STATE_COLORS = {
  idle: "#38d8ff",
  listening: "#52f7ff",
  thinking: "#7a8cff",
  speaking: "#45fff0",
  working: "#26c8ff",
  error: "#ff4e66",
};

export default function EnergyCore({ coreState = "idle" }) {
  const meshRef = useRef(null);
  const glowRef = useRef(null);
  const profile = getCoreMotionProfile(coreState);
  const color = STATE_COLORS[profile.state] ?? STATE_COLORS.idle;

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();
    const pulse = 1 + Math.sin(t * (2.4 + profile.rotationSpeed * 8)) * profile.pulse;
    if (meshRef.current) {
      meshRef.current.scale.setScalar(pulse * profile.scale);
      meshRef.current.rotation.y += profile.rotationSpeed * 0.01;
      meshRef.current.rotation.x = Math.sin(t * 0.35) * 0.08;
    }
    if (glowRef.current) {
      glowRef.current.scale.setScalar((1.42 + Math.sin(t * 1.6) * 0.05) * profile.scale);
    }
  });

  return (
    <group>
      <mesh ref={glowRef}>
        <sphereGeometry args={[1.26, 48, 48]} />
        <meshBasicMaterial color={color} transparent opacity={0.055} depthWrite={false} />
      </mesh>
      <mesh ref={meshRef}>
        <icosahedronGeometry args={[0.92, 5]} />
        <meshStandardMaterial color="#071524" emissive={color} emissiveIntensity={3.8} roughness={0.12} metalness={0.5} transparent opacity={0.96} wireframe />
      </mesh>
      <mesh scale={0.58}>
        <sphereGeometry args={[1, 40, 40]} />
        <meshBasicMaterial color={color} transparent opacity={0.55} />
      </mesh>
      <pointLight color={color} intensity={8} distance={7} decay={2} />
    </group>
  );
}
