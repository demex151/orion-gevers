import { Canvas } from "@react-three/fiber";
import { Float } from "@react-three/drei";
import EnergyCore from "./EnergyCore.jsx";
import HolographicRings from "./HolographicRings.jsx";
import OrbitLines from "./OrbitLines.jsx";
import ParticleField from "./ParticleField.jsx";

function Scene({ coreState }) {
  return (
    <>
      <ambientLight intensity={0.18} />
      <directionalLight position={[3, 4, 5]} color="#7bdfff" intensity={1.2} />
      <Float speed={0.7} rotationIntensity={0.06} floatIntensity={0.16}>
        <group rotation={[0.08, -0.14, 0]}>
          <ParticleField coreState={coreState} />
          <OrbitLines />
          <HolographicRings coreState={coreState} />
          <EnergyCore coreState={coreState} />
        </group>
      </Float>
    </>
  );
}

export default function GeverCore3D({ coreState = "idle" }) {
  return (
    <div className={`gever-core-3d core-state-${coreState}`} aria-label={`Núcleo GEVER: ${coreState}`}>
      <Canvas
        dpr={[1, 1.75]}
        camera={{ position: [0, 0.15, 7.5], fov: 38, near: 0.1, far: 100 }}
        gl={{ antialias: true, alpha: true, powerPreference: "high-performance" }}
        fallback={<div className="gever-core-fallback">Núcleo 3D no disponible</div>}
      >
        <Scene coreState={coreState} />
      </Canvas>
      <div className="core-reticle" aria-hidden="true"><span /><span /><span /><span /></div>
    </div>
  );
}
