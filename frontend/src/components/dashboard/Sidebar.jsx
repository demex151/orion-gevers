const ITEMS = [
  ["⌂", "Inicio", "inicio"], ["◉", "Conversaciones", "conversaciones"], ["⬢", "Sistema", "sistema"],
  ["⬡", "Agentes", "agentes"], ["◇", "Conocimiento", "memoria"], ["☷", "Analítica", "analitica"],
  ["▣", "Calendario", "calendario"], ["✉", "Comunicaciones", "comunicaciones"], ["⚙", "Ajustes", "ajustes"],
];

export default function Sidebar({ activeSection = "inicio", onNavigate }) {
  return <aside className="gever-sidebar">
    <div className="hud-brand"><div className="hud-brand-mark">G</div><div><strong>GEVER</strong><small>INTELLIGENCE SYSTEM</small></div></div>
    <nav>{ITEMS.map(([icon,label,section]) => <button key={section} className={activeSection === section ? "active" : ""} onClick={() => onNavigate?.(section)}><span>{icon}</span><b>{label}</b></button>)}</nav>
    <div className="hud-core-card"><span className="hud-core-dot">◉</span><div><b>Núcleo AI</b><small>● ACTIVO</small></div></div>
  </aside>;
}
