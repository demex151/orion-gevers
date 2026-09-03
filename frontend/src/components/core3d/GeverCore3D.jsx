import { useEffect, useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Float } from "@react-three/drei";
import EnergyCore from "./EnergyCore.jsx";
import HolographicRings from "./HolographicRings.jsx";
import OrbitLines from "./OrbitLines.jsx";
import ParticleField from "./ParticleField.jsx";
import { GEVER_GESTURE_EVENT } from "../../gestures/gestureCommands.js";

function CoreRig({ coreState }) {
  const rigRef = useRef(null);
  const scanRef = useRef(null);
  const target = useRef({ rx: 0.08, ry: -0.14, scale: 1 });

  useEffect(() => {
    function handleGesture(event) {
      const command = event.detail || {};
      if (command.type === "rotate") {
        target.current.rx += Number(command.value?.x || 0) * 0.12;
        target.current.ry += Number(command.value?.y || 0) * 0.12;
      } else if (command.type === "zoom") {
        target.current.scale = Number(command.value || 1);
      } else if (command.type === "reset-view") {
        target.current = { rx: 0.08, ry: -0.14, scale: 1 };
      }
    }
    window.addEventListener(GEVER_GESTURE_EVENT, handleGesture);
    return () => window.removeEventListener(GEVER_GESTURE_EVENT, handleGesture);
  }, []);

  useFrame(({ clock }) => {
    if (!rigRef.current) return;
    rigRef.current.rotation.x += (target.current.rx - rigRef.current.rotation.x) * 0.075;
    rigRef.current.rotation.y += (target.current.ry - rigRef.current.rotation.y) * 0.075;
    const nextScale = rigRef.current.scale.x + (target.current.scale - rigRef.current.scale.x) * 0.075;
    rigRef.current.scale.setScalar(nextScale);
    if (scanRef.current) {
      scanRef.current.position.y = Math.sin(clock.getElapsedTime() * 0.72) * 1.7;
      scanRef.current.material.opacity = 0.055 + Math.abs(Math.sin(clock.getElapsedTime() * 0.72)) * 0.05;
    }
  });

  return <group ref={rigRef} rotation={[0.08, -0.14, 0]}>
    <ParticleField coreState={coreState} />
    <OrbitLines />
    <HolographicRings coreState={coreState} />
    <EnergyCore coreState={coreState} />

    <mesh ref={scanRef} rotation={[Math.PI / 2, 0, 0]}>
      <ringGeometry args={[0.7, 2.65, 96]} />
      <meshBasicMaterial color="#5be9ff" transparent opacity={0.07} depthWrite={false} side={2} />
    </mesh>

    <mesh rotation={[Math.PI / 2, 0, 0]} position={[0, -2.25, 0]}>
      <ringGeometry args={[1.45, 2.95, 128]} />
      <meshBasicMaterial color="#2c9dff" transparent opacity={0.08} depthWrite={false} side={2} />
    </mesh>
    <mesh rotation={[Math.PI / 2, 0, 0]} position={[0, -2.24, 0]}>
      <torusGeometry args={[2.15, 0.018, 8, 160]} />
      <meshBasicMaterial color="#69ecff" transparent opacity={0.38} depthWrite={false} />
    </mesh>
  </group>;
}

function Scene({ coreState }) {
  return <>
    <ambientLight intensity={0.16} />
    <directionalLight position={[3, 4, 5]} color="#7bdfff" intensity={1.25} />
    <directionalLight position={[-4, -2, 3]} color="#315cff" intensity={0.62} />
    <Float speed={0.68} rotationIntensity={0.055} floatIntensity={0.15}>
      <CoreRig coreState={coreState} />
    </Float>
  </>;
}

export default function GeverCore3D({ coreState = "idle" }) {
  return <div className={`gever-core-3d core-state-${coreState}`} aria-label={`Núcleo GEVER: ${coreState}`}>
    <Canvas
      dpr={[1, 1.75]}
      camera={{ position: [0, 0.2, 7.85], fov: 36, near: 0.1, far: 100 }}
      gl={{ antialias: true, alpha: true, powerPreference: "high-performance" }}
      fallback={<div className="gever-core-fallback">Núcleo 3D no disponible</div>}
    >
      <Scene coreState={coreState} />
    </Canvas>
    <div className="core-reticle" aria-hidden="true"><span /><span /><span /><span /></div>
    <div className="core-hud-axis core-hud-axis-x" aria-hidden="true" />
    <div className="core-hud-axis core-hud-axis-y" aria-hidden="true" />
  </div>;
}
