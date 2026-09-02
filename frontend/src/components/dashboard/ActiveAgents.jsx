export default function ActiveAgents({ agents = [] }) {
  return <section className="hud-panel active-agents">
    <div className="hud-panel-title"><span>AGENTES ACTIVOS</span><i>{agents.length}/7</i></div>
    <div className="agent-stack">{agents.map(([icon,name,desc]) => <div className="agent-row" key={name}><div className="agent-icon">{icon}</div><div><b>{name}</b><small>{desc}</small></div><span className="agent-live">●</span></div>)}</div>
    <button className="hud-link">GESTIONAR AGENTES <span>→</span></button>
  </section>;
}
