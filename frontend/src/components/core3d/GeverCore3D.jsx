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

  useFrame(() => {
    if (!rigRef.current) return;
    rigRef.current.rotation.x += (target.current.rx - rigRef.current.rotation.x) * 0.075;
    rigRef.current.rotation.y += (target.current.ry - rigRef.current.rotation.y) * 0.075;
    const nextScale = rigRef.current.scale.x + (target.current.scale - rigRef.current.scale.x) * 0.075;
    rigRef.current.scale.setScalar(nextScale);
  });

  return <group ref={rigRef} rotation={[0.08, -0.14, 0]}>
    <ParticleField coreState={coreState} />
    <OrbitLines />
    <HolographicRings coreState={coreState} />
    <EnergyCore coreState={coreState} />
  </group>;
}

function Scene({ coreState }) {
  return <>
    <ambientLight intensity={0.18} />
    <directionalLight position={[3, 4, 5]} color="#7bdfff" intensity={1.2} />
    <Float speed={0.7} rotationIntensity={0.06} floatIntensity={0.16}>
      <CoreRig coreState={coreState} />
    </Float>
  </>;
}

export default function GeverCore3D({ coreState = "idle" }) {
  return <div className={`gever-core-3d core-state-${coreState}`} aria-label={`Núcleo GEVER: ${coreState}`}>
    <Canvas
      dpr={[1, 1.75]}
      camera={{ position: [0, 0.15, 7.5], fov: 38, near: 0.1, far: 100 }}
      gl={{ antialias: true, alpha: true, powerPreference: "high-performance" }}
      fallback={<div className="gever-core-fallback">Núcleo 3D no disponible</div>}
    >
      <Scene coreState={coreState} />
    </Canvas>
    <div className="core-reticle" aria-hidden="true"><span /><span /><span /><span /></div>
  </div>;
}
