export default function GreetingHeader({ status = "Escuchando" }) {
  return <header className="gever-topbar">
    <div><span className="system-live">● SISTEMA OPERATIVO</span><span className="system-check">● TODO BAJO CONTROL</span></div>
    <div className="topbar-actions"><button aria-label="Buscar">⌕</button><button aria-label="Panel">▦</button><button aria-label="Herramientas">◇</button><button className="topbar-add" aria-label="Nuevo">+</button></div>
    <div className="topbar-status">{status}</div>
  </header>;
}
