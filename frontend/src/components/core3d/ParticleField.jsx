import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { getCoreMotionProfile } from "./CoreStateController.js";

export default function ParticleField({ coreState = "idle", count = 340 }) {
  const pointsRef = useRef(null);
  const profile = getCoreMotionProfile(coreState);
  const positions = useMemo(() => {
    const data = new Float32Array(count * 3);
    for (let i = 0; i < count; i += 1) {
      const radius = 2.2 + Math.random() * 2.8;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      data[i * 3] = radius * Math.sin(phi) * Math.cos(theta);
      data[i * 3 + 1] = radius * Math.cos(phi) * 0.72;
      data[i * 3 + 2] = radius * Math.sin(phi) * Math.sin(theta);
    }
    return data;
  }, [count]);

  useFrame((_, delta) => {
    if (!pointsRef.current) return;
    pointsRef.current.rotation.y += delta * (0.025 + profile.particleEnergy * 0.05);
    pointsRef.current.rotation.x += delta * 0.006;
  });

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" args={[positions, 3]} />
      </bufferGeometry>
      <pointsMaterial color="#62eaff" size={0.025 + profile.particleEnergy * 0.018} transparent opacity={0.48 + profile.particleEnergy * 0.24} depthWrite={false} sizeAttenuation />
    </points>
  );
}
