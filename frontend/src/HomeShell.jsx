import { useEffect, useState } from "react";
import App from "./App.jsx";
import GeverCore3D from "./components/core3d/GeverCore3D.jsx";
import Sidebar from "./components/dashboard/Sidebar.jsx";
import GreetingHeader from "./components/dashboard/GreetingHeader.jsx";
import SystemMetrics from "./components/dashboard/SystemMetrics.jsx";
import ActiveAgents from "./components/dashboard/ActiveAgents.jsx";
import GesturePanel from "./components/dashboard/GesturePanel.jsx";
import CommandBar from "./components/dashboard/CommandBar.jsx";
import SystemFooter from "./components/dashboard/SystemFooter.jsx";
import { GEVER_VISUAL_EVENT } from "./geverVisualBridge.js";
import { normalizeCoreState } from "./coreState.js";
import "./HomeShellFix.css";
import "./styles/gever-dashboard.css";

const API = "http://127.0.0.1:8000";
const agents = [
  ["⌕", "Analista de datos", "Procesando información"],
  ["▦", "Estratega de negocio", "Optimizando estrategia"],
  ["◇", "Creador de contenido", "Generando contenido"],
  ["⌁", "Asistente de investigación", "Buscando información"],
  ["◫", "Analista financiero", "Evaluando métricas"],
];

const LEGACY_LABELS = {
  conversaciones: "Conversaciones",
  sistema: "Sistema",
  agentes: "Agentes",
  memoria: "Memoria",
  analitica: "Analítica",
  calendario: "Calendario",
  comunicaciones: "Comunicaciones",
  ajustes: "Ajustes",
};

function clickLegacyNav(label) {
  Array.from(document.querySelectorAll(".legacy-app .nav-item"))
    .find((button) => button.textContent?.toLowerCase().includes(label.toLowerCase()))
    ?.click();
}

export default function HomeShell() {
  const [homeVisible, setHomeVisible] = useState(true);
  const [activeSection, setActiveSection] = useState("inicio");
  const [command, setCommand] = useState("");
  const [status, setStatus] = useState("Escuchando");
  const [coreState, setCoreState] = useState("listening");
  const [busy, setBusy] = useState(false);

  function applyStatus(nextStatus) {
    const next = String(nextStatus || "").trim() || "En espera";
    setStatus(next === "ESPERANDO ORION" ? "Escuchando" : next);
    setCoreState(normalizeCoreState(next === "ESPERANDO ORION" ? "Escuchando" : next));
  }

  useEffect(() => {
    function handleVisualState(event) {
      if (busy) return;
      const detail = event.detail || {};
      if (detail.status) {
        setStatus(detail.status);
        setCoreState(detail.coreState || normalizeCoreState(detail.status));
      }
    }
    window.addEventListener(GEVER_VISUAL_EVENT, handleVisualState);
    return () => window.removeEventListener(GEVER_VISUAL_EVENT, handleVisualState);
  }, [busy]);

  useEffect(() => {
    const timer = setInterval(() => {
      if (busy) return;
      const legacyStatus = document.querySelector(".legacy-app .core-status")?.textContent?.trim();
      if (legacyStatus) applyStatus(legacyStatus);
    }, 350);
    return () => clearInterval(timer);
  }, [busy]);

  function openSection(section) {
    setActiveSection(section);
    if (section === "inicio") {
      clickLegacyNav("Inicio");
      setHomeVisible(true);
      return;
    }
    const legacyLabel = LEGACY_LABELS[section];
    if (legacyLabel) clickLegacyNav(legacyLabel);
    setHomeVisible(false);
  }

  async function speak(text) {
    applyStatus("Preparando voz");
    const response = await fetch(`${API}/api/tts`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    if (!response.ok) throw new Error(`TTS respondió ${response.status}`);
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const audio = new Audio(url);
    await new Promise((resolve, reject) => {
      audio.onplaying = () => applyStatus("Hablando");
      audio.onended = () => { URL.revokeObjectURL(url); resolve(); };
      audio.onerror = () => { URL.revokeObjectURL(url); reject(new Error("No se pudo reproducir la voz")); };
      audio.play().catch(reject);
    });
  }

  async function sendCommand() {
    const value = command.trim();
    if (!value || busy) return;
    setBusy(true);
    setCommand("");
    applyStatus("Pensando");
    try {
      const response = await fetch(`${API}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: value }),
      });
      if (!response.ok) throw new Error(`Chat respondió ${response.status}`);
      const data = await response.json();
      if (data?.ok === false) throw new Error(data.error || "GEVER no pudo responder");
      const answer = String(data?.answer || "").trim();
      if (!answer) throw new Error("GEVER respondió vacío");
      await speak(answer);
      applyStatus("Escuchando");
    } catch (error) {
      console.error("[GEVER HOME]", error);
      applyStatus("Error de conexión");
    } finally {
      setBusy(false);
    }
  }

  function quickCommand(text) {
    setCommand(text);
  }

  return <div className="gever-shell-root">
    <div className={homeVisible ? "legacy-app legacy-hidden" : "legacy-app legacy-visible"}><App /></div>
    {homeVisible && <main className="gever-dashboard">
      <div className="hud-frame-corners" aria-hidden="true"><i/><i/><i/><i/></div>
      <Sidebar activeSection={activeSection} onNavigate={openSection} />
      <GreetingHeader status={status} />
      <SystemMetrics cpu={42} memory={68} network={23} status="Óptimo" />

      <section className="gever-core-stage">
        <div className="core-title"><h1>NÚCLEO HOLOGRÁFICO GEVER</h1><p>INTELIGENCIA • VOZ • AUTOMATIZACIÓN</p></div>
        <div className="core-telemetry core-telemetry-left" aria-hidden="true"><span>AI CORE</span><b>ONLINE</b><small>LAT 12MS</small></div>
        <div className="core-telemetry core-telemetry-right" aria-hidden="true"><span>VOICE LINK</span><b>STABLE</b><small>SYNC 99.8%</small></div>
        <div className="core-index core-index-a" aria-hidden="true">01</div>
        <div className="core-index core-index-b" aria-hidden="true">GEV-7</div>
        <GeverCore3D coreState={coreState} />
        <div className="core-caption"><span>{status}</span><span className="core-caption-wave"><i/><i/><i/><i/></span></div>
      </section>

      <aside className="gever-right-rail">
        <ActiveAgents agents={agents} />
        <GesturePanel enabled={false} lastGesture="PREPARADO" />
      </aside>

      <section className="gever-command-zone">
        <CommandBar value={command} onChange={setCommand} onSubmit={sendCommand} busy={busy} />
        <div className="quick-actions">
          <button onClick={() => quickCommand("Analiza los datos del negocio de hoy")}>⌕ ANALIZAR DATOS</button>
          <button onClick={() => quickCommand("Genera un informe ejecutivo")}>◇ GENERAR INFORME</button>
          <button onClick={() => quickCommand("Revisa la estrategia actual")}>▦ REVISAR ESTRATEGIA</button>
          <button onClick={() => quickCommand("Crea contenido para redes sociales")}>••• CREAR CONTENIDO</button>
        </div>
      </section>

      <SystemFooter coreState={coreState} status={status} />
    </main>}
  </div>;
}
