export default function GesturePanel({ enabled = false, lastGesture = "Ninguno" }) {
  return <section className="hud-panel gesture-panel">
    <div className="hud-panel-title"><span>CONTROL GESTUAL</span><i>{enabled ? "READY" : "PREPARED"}</i></div>
    <div className="gesture-hand" aria-hidden="true"><span>◇</span><i className="gesture-ring r1"/><i className="gesture-ring r2"/></div>
    <div className="gesture-grid"><div><span>CÁMARA</span><b>{enabled ? "ACTIVA" : "PENDIENTE"}</b></div><div><span>GESTO</span><b>{lastGesture}</b></div></div>
    <small className="gesture-note">Interfaz preparada para control 3D por manos.</small>
  </section>;
}
