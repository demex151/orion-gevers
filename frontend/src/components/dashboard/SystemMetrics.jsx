export default function SystemMetrics({ cpu = 42, memory = 68, network = 23, status = "Óptimo" }) {
  const rows = [["CPU", cpu], ["MEMORIA", memory], ["RED", network]];
  return <section className="hud-panel system-metrics">
    <div className="hud-panel-title"><span>ESTADO DEL SISTEMA</span><i>SYS-01</i></div>
    <div className="metric-orbit"><div className="metric-orbit-core"><strong>98%</strong><small>{status}</small></div></div>
    <div className="metric-list">{rows.map(([label,value]) => <div key={label} className="metric-row"><div><span>{label}</span><b>{value}%</b></div><div className="metric-track"><i style={{ width: `${value}%` }} /></div></div>)}</div>
    <div className="hud-panel-foot"><span>RENDIMIENTO</span><b>EXCELENTE</b></div>
  </section>;
}
