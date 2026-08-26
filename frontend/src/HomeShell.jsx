import { useEffect, useMemo, useState } from "react";
import App from "./App.jsx";
import "./HomeShell.css";

const navItems = [
  ["⌂", "Inicio", "inicio"],
  ["◉", "Conversaciones", "conversaciones"],
  ["⚙", "Sistema", "sistema"],
  ["⬡", "Agentes", "agentes"],
  ["◇", "Conocimiento", "memoria"],
  ["☷", "Analítica", "analitica"],
  ["▣", "Calendario", "calendario"],
  ["✉", "Comunicaciones", "comunicaciones"],
  ["⚙", "Ajustes", "ajustes"],
];

const activityRows = [
  ["▧", "Informe de rendimiento mensual", "Completado", "22:15"],
  ["▥", "Análisis de mercado", "Completado", "21:40"],
  ["◇", "Estrategia de crecimiento", "Completado", "20:30"],
  ["▣", "Reporte de clientes", "Completado", "19:55"],
  ["⌁", "Pronóstico financiero", "Completado", "18:20"],
];

const agents = [
  ["◉", "Analista de datos", "Procesando información"],
  ["◇", "Estratega de negocio", "Optimizando estrategia"],
  ["▣", "Creador de contenido", "Generando contenido"],
  ["▢", "Asistente de investigación", "Buscando información"],
  ["◈", "Analista financiero", "Evaluando métricas"],
];

function nativeSetInputValue(input, value) {
  const setter = Object.getOwnPropertyDescriptor(
    window.HTMLInputElement.prototype,
    "value",
  )?.set;

  if (setter) setter.call(input, value);
  else input.value = value;

  input.dispatchEvent(new Event("input", { bubbles: true }));
}

function clickLegacyNav(label) {
  const buttons = Array.from(document.querySelectorAll(".legacy-app .nav-item"));
  const target = buttons.find((button) =>
    button.textContent?.toLowerCase().includes(label.toLowerCase()),
  );
  target?.click();
}

export default function HomeShell() {
  const [homeVisible, setHomeVisible] = useState(true);
  const [command, setCommand] = useState("");
  const [status, setStatus] = useState("ESPERANDO ORION");

  useEffect(() => {
    const timer = window.setInterval(() => {
      const legacyStatus = document.querySelector(".legacy-app .core-status")?.textContent?.trim();
      if (legacyStatus) setStatus(legacyStatus);
    }, 250);

    return () => window.clearInterval(timer);
  }, []);

  const isListening = useMemo(
    () => /ESCUCHANDO|RESPONDIENDO|PROCESANDO|PREPARANDO/i.test(status),
    [status],
  );

  function openSection(section) {
    if (section === "inicio") {
      clickLegacyNav("Inicio");
      setHomeVisible(true);
      return;
    }

    if (section === "memoria") {
      clickLegacyNav("Memoria");
      setHomeVisible(false);
      return;
    }
  }

  function toggleVoice() {
    document.querySelector(".legacy-app .talk-button")?.click();
  }

  function sendCommand() {
    const value = command.trim();
    if (!value) return;

    const input = document.querySelector(".legacy-app .command-input input");
    const button = document.querySelector(".legacy-app .send-button");

    if (!input || !button) return;

    nativeSetInputValue(input, value);
    window.setTimeout(() => button.click(), 0);
    setCommand("");
  }

  function onCommandKeyDown(event) {
    if (event.key === "Enter") {
      event.preventDefault();
      sendCommand();
    }
  }

  return (
    <div className="gever-shell-root">
      <div className={homeVisible ? "legacy-app legacy-hidden" : "legacy-app legacy-visible"}>
        <App />
      </div>

      {homeVisible && (
        <div className="reference-home">
          <aside className="reference-sidebar">
            <div className="reference-logo">
              <div className="reference-logo-icon">G</div>
              <div>
                <strong>GEVER</strong>
                <span>INTELLIGENCE SYSTEM</span>
              </div>
            </div>

            <nav className="reference-nav">
              {navItems.map(([icon, label, section], index) => (
                <button
                  key={label}
                  className={index === 0 ? "reference-nav-item active" : "reference-nav-item"}
                  onClick={() => openSection(section)}
                  type="button"
                >
                  <span>{icon}</span>
                  {label}
                </button>
              ))}
            </nav>

            <div className="reference-core-mini">
              <div className="mini-orb">◉</div>
              <div>
                <strong>Núcleo AI</strong>
                <span>● Activo</span>
              </div>
            </div>
          </aside>

          <header className="reference-topbar">
            <div className="status-pills">
              <span>● Sistema operativo</span>
              <span>● Todo bajo control</span>
            </div>
            <div className="reference-tools">⌕ &nbsp; ⠿ &nbsp; ♧ &nbsp; <b>+</b></div>
          </header>

          <section className="system-card glass-card">
            <div className="small-card-title">Sistema operativo <span>•••</span></div>
            <div className="os-gauge">
              <div className="os-gauge-inner"><strong>98%</strong><span>Óptimo</span></div>
            </div>
            <div className="system-stats">
              <div><span>CPU</span><b>42%</b></div>
              <div><span>Memoria</span><b>68%</b></div>
              <div><span>Red</span><b>23%</b></div>
              <div><span>Almacenamiento</span><b>71%</b></div>
            </div>
            <div className="card-divider" />
            <div className="system-footer"><span>Rendimiento del sistema</span><b>Excelente</b></div>
          </section>

          <section className="growth-card glass-card">
            <div className="small-card-title"><div><b>Crecimiento</b><small>Resumen de 30 días</small></div><span>⠿</span></div>
            <div className="growth-main">+24.6%</div>
            <div className="growth-sub">vs. período anterior</div>
            <svg className="growth-line" viewBox="0 0 220 64" preserveAspectRatio="none" aria-hidden="true">
              <polyline points="0,52 25,44 45,50 70,33 92,39 118,25 145,30 170,18 195,24 220,8" fill="none" stroke="url(#growthGradient)" strokeWidth="2" />
              <defs><linearGradient id="growthGradient" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stopColor="#2de9ff"/><stop offset="1" stopColor="#9b64ff"/></linearGradient></defs>
            </svg>
            <div className="growth-rows">
              <div><span>Ingresos</span><b>$ 128,450<small>+18.2%</small></b></div>
              <div><span>Clientes nuevos</span><b>342<small>+27.1%</small></b></div>
              <div><span>Retención</span><b>92%<small>+8.4%</small></b></div>
            </div>
          </section>

          <main className="reference-center">
            <div className="reference-greeting">
              <h1>Buenas noches, José</h1>
              <p>¿En qué trabajamos hoy?</p>
            </div>

            <div className={`reference-orb ${isListening ? "active" : ""}`}>
              <div className="orb-ring ring-a" />
              <div className="orb-ring ring-b" />
              <div className="orb-ring ring-c" />
              <div className="orb-axis horizontal" />
              <div className="orb-axis vertical" />
              <div className="orb-globe"><div className="orb-star">✦</div></div>
            </div>

            <div className="reference-listening">
              <div className="wave left"><i/><i/><i/><i/><i/><i/><i/></div>
              <strong>{status.replace("ESPERANDO ORION", "Escuchando")}</strong>
              <div className="wave right"><i/><i/><i/><i/><i/><i/><i/></div>
            </div>

            <div className="reference-command">
              <input
                value={command}
                onChange={(event) => setCommand(event.target.value)}
                onKeyDown={onCommandKeyDown}
                placeholder="Escribe tu solicitud o comando..."
              />
              <button type="button" onClick={sendCommand}>↑</button>
            </div>

            <div className="reference-quick-actions">
              <button type="button">⌕ &nbsp; Analizar datos</button>
              <button type="button">♢ &nbsp; Generar informe</button>
              <button type="button">⠿ &nbsp; Revisar estrategia</button>
              <button type="button">••• &nbsp; Crear contenido</button>
            </div>

            <section className="calendar-card lower-card">
              <div className="lower-title"><b>Calendario</b><span>Viernes, 23 de mayo</span></div>
              {[["09:00","Reunión de estrategia"],["11:30","Revisión de resultados"],["14:00","Presentación de proyecto"],["16:30","Análisis de mercado"]].map(([time,title],i)=>(
                <div className="calendar-row" key={time}><i className={`dot dot-${i}`}/><span>{time}</span><b>{title}</b></div>
              ))}
            </section>

            <section className="communications-card lower-card">
              <div className="lower-title"><b>Comunicaciones</b><span>⠿</span></div>
              {[["M","María González","Actualización del proyecto Q2","22:30"],["C","Carlos Ramírez","Revisión del informe financiero","21:15"],["A","Ana López","Estrategia de marketing digital","20:50"]].map(([initial,name,desc,time],i)=>(
                <div className="comm-row" key={name}><i className={`avatar avatar-${i}`}>{initial}</i><div><b>{name}</b><span>{desc}</span></div><time>{time}</time></div>
              ))}
            </section>
          </main>

          <aside className="recent-card glass-card">
            <div className="right-card-title">Actividad reciente <span>•••</span></div>
            <div className="right-list">
              {activityRows.map(([icon,title,sub,time]) => (
                <div className="right-row" key={title}><i>{icon}</i><div><b>{title}</b><span>{sub}</span></div><time>{time}</time></div>
              ))}
            </div>
            <div className="right-footer">Ver toda la actividad <span>›</span></div>
          </aside>

          <aside className="agents-card glass-card">
            <div className="right-card-title">Agentes activos <span>5/7</span></div>
            <div className="right-list agents-list">
              {agents.map(([icon,title,sub]) => (
                <div className="right-row" key={title}><i>{icon}</i><div><b>{title}</b><span>{sub}</span></div><em>●</em></div>
              ))}
            </div>
            <button type="button" className="right-footer button-footer" onClick={toggleVoice}>Gestionar agentes <span>›</span></button>
          </aside>
        </div>
      )}
    </div>
  );
}
