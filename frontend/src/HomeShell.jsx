import { useEffect, useState } from "react";
import App from "./App.jsx";
import { createSubtitleChunks, subtitleAtTime } from "./speechVisuals.js";
import "./HomeShellFix.css";

const API="http://127.0.0.1:8000";
const FIGMA_BG="https://www.figma.com/api/mcp/asset/35c2b6c1-77e1-4593-98b7-ac82a2b0d542";
const FIGMA_BG_ALT="https://www.figma.com/api/mcp/asset/16911c84-b5b0-4d39-9f40-c04cafd4f426.png";
const ORB_OUTER_1="https://www.figma.com/api/mcp/asset/9dac0c5f-cac6-4862-8608-dda298b68f8e.svg";
const ORB_OUTER_2="https://www.figma.com/api/mcp/asset/81f89820-7336-4bb4-86c9-67175c45cf42.png";
const ORB_MEDIUM="https://www.figma.com/api/mcp/asset/d2898649-77eb-40c3-bbc8-10b68d42a12f.svg";
const ORB_AXIS="https://www.figma.com/api/mcp/asset/d0dc8d15-413b-4cbc-b0b5-1923e20cfd36.svg";
const ORB_DOT="https://www.figma.com/api/mcp/asset/ecf73cad-bd21-4785-97c7-992d80799866.svg";
const ORB_HALO_1="https://www.figma.com/api/mcp/asset/9533c683-6812-4be8-8b36-7c2cada52e3b.svg";
const ORB_HALO_2="https://www.figma.com/api/mcp/asset/1765fa91-ce21-4925-b521-e5599c6eb1fe.svg";
const ORB_GLOBE="https://www.figma.com/api/mcp/asset/bf57169a-646e-4f3b-aeb6-5de55842c272.png";
const ORB_FLARE="https://www.figma.com/api/mcp/asset/1f7197f5-78a5-4ec6-833c-a5b853d84351.svg";

const navItems=[["⌂","Inicio","inicio"],["◉","Conversaciones","conversaciones"],["⚙","Sistema","sistema"],["⬡","Agentes","agentes"],["◇","Conocimiento","memoria"],["☷","Analítica","analitica"],["📅","Calendario","calendario"],["✉","Comunicaciones","comunicaciones"],["⚙","Ajustes","ajustes"]];
const agents=[["⌕","Analista de datos","Procesando información"],["▦","Estratega de negocio","Optimizando estrategia"],["♧","Creador de contenido","Generando contenido"],["⌕","Asistente de investigación","Buscando información"],["▦","Analista financiero","Evaluando métricas"]];

function clickLegacyNav(label){Array.from(document.querySelectorAll(".legacy-app .nav-item")).find(b=>b.textContent?.toLowerCase().includes(label.toLowerCase()))?.click();}

export default function HomeShell(){
  const[homeVisible,setHomeVisible]=useState(true);
  const[command,setCommand]=useState("");
  const[status,setStatus]=useState("Escuchando");
  const[busy,setBusy]=useState(false);
  const[subtitle,setSubtitle]=useState("");
  const[speaking,setSpeaking]=useState(false);

  useEffect(()=>{const timer=setInterval(()=>{if(busy)return;const s=document.querySelector(".legacy-app .core-status")?.textContent?.trim();if(s)setStatus(s==="ESPERANDO ORION"?"Escuchando":s)},250);return()=>clearInterval(timer)},[busy]);

  function openSection(section){if(section==="inicio"){clickLegacyNav("Inicio");setHomeVisible(true);return}if(section==="memoria"){clickLegacyNav("Memoria");setHomeVisible(false)}}

  async function speak(text){
    const chunks=createSubtitleChunks(text);
    setSubtitle(chunks[0]||"");
    setStatus("Preparando voz");
    const response=await fetch(`${API}/api/tts`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({text})});
    if(!response.ok)throw new Error(`TTS respondió ${response.status}`);
    const blob=await response.blob();
    const url=URL.createObjectURL(blob);
    const audio=new Audio(url);
    await new Promise((resolve,reject)=>{
      audio.onplaying=()=>{setSpeaking(true);setStatus("Hablando")};
      audio.ontimeupdate=()=>setSubtitle(subtitleAtTime(chunks,audio.currentTime,audio.duration));
      audio.onended=()=>{setSpeaking(false);setSubtitle("");URL.revokeObjectURL(url);resolve()};
      audio.onerror=()=>{setSpeaking(false);setSubtitle("");URL.revokeObjectURL(url);reject(new Error("No se pudo reproducir la voz"))};
      audio.play().catch(error=>{setSpeaking(false);setSubtitle("");reject(error)});
    });
  }

  async function sendCommand(){
    const value=command.trim();
    if(!value||busy)return;
    setBusy(true);setCommand("");setStatus("Pensando");setSubtitle("");
    try{
      const response=await fetch(`${API}/api/chat`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:value})});
      if(!response.ok)throw new Error(`Chat respondió ${response.status}`);
      const data=await response.json();
      if(data?.ok===false)throw new Error(data.error||"GEVER no pudo responder");
      const answer=String(data?.answer||"").trim();
      if(!answer)throw new Error("GEVER respondió vacío");
      setSubtitle(createSubtitleChunks(answer)[0]||answer);
      await speak(answer);
      setStatus("Escuchando");
    }catch(error){console.error("[GEVER HOME]",error);setSpeaking(false);setSubtitle("");setStatus("Error de conexión")}
    finally{setBusy(false)}
  }

  const thinking=busy&&!speaking;

  return <div className="gever-shell-root">
    <div className={homeVisible?"legacy-app legacy-hidden":"legacy-app legacy-visible"}><App/></div>
    {homeVisible&&<div className="figma-home" data-node-id="2004:3">
      <img className="figma-background" src={FIGMA_BG} onError={e=>{if(e.currentTarget.src!==FIGMA_BG_ALT)e.currentTarget.src=FIGMA_BG_ALT}} alt=""/>
      <div className="figma-focus-ring"/>
      <div className="figma-logo"><div className="figma-logo-icon">G</div><div><b>GEVER</b><small>INTELLIGENCE SYSTEM</small></div></div>
      <nav className="figma-nav">{navItems.map(([icon,label,section],i)=><button key={label} className={i===0?"active":""} onClick={()=>openSection(section)}><span>{icon}</span><b>{label}</b></button>)}</nav>
      <div className="figma-core-card"><div className="figma-core-orb">◉</div><div><b>Núcleo AI</b><small>● Activo</small></div></div>
      <header className="figma-header"><div className="figma-status"><span>● Sistema operativo</span><span>● Todo bajo control</span></div><div className="figma-toolbar"><span>⌕</span><span>▦</span><span>♧</span><b>+</b></div></header>
      <section className="figma-os figma-panel"><div className="figma-panel-head"><b>Sistema operativo</b><span>•••</span></div><div className="figma-donut"><div><b>98%</b><small>Óptimo</small></div></div><div className="figma-stats">{[["CPU","42%"],["Memoria","68%"],["Red","23%"],["Almacenamiento","71%"]].map(([a,b])=><p key={a}><span>{a}</span><b>{b}</b></p>)}</div><hr/><div className="figma-panel-foot"><span>Rendimiento del sistema</span><b>Excelente</b></div></section>
      <section className="figma-growth figma-panel"><div className="figma-panel-head"><div><b>Crecimiento</b><small>Resumen de 30 días</small></div><span>▦</span></div><strong className="figma-growth-number">+24.6%</strong><small className="figma-muted">vs. período anterior</small><svg className="figma-spark" viewBox="0 0 222 50"><polyline points="0,39 22,34 43,39 66,25 89,30 112,18 136,22 158,12 185,17 222,4" fill="none" stroke="#61e8ff" strokeWidth="2"/></svg><hr/><div className="figma-growth-rows">{[["Ingresos","$ 128,450","+18.2%"],["Clientes nuevos","342","+27.1%"],["Retención","92%","+8.4%"]].map(([a,b,c])=><p key={a}><span>{a}</span><b>{b}<small>{c}</small></b></p>)}</div></section>
      <div className={`figma-greeting ${subtitle?"speaking-copy":""}`}><h1>{subtitle||"Buenas noches, José"}</h1><p>{subtitle?(speaking?"GEVER está hablando":status):"¿En qué trabajamos hoy?"}</p></div>
      <div className={`figma-orb-visualizer ${speaking?"is-speaking":""} ${thinking?"is-thinking":""}`}><div className="figma-orb-wrap"><img className="orb outer1" src={ORB_OUTER_1} alt=""/><img className="orb outer2" src={ORB_OUTER_2} alt=""/><img className="orb medium" src={ORB_MEDIUM} alt=""/><img className="orb axis" src={ORB_AXIS} alt=""/><img className="orb dot left" src={ORB_DOT} alt=""/><img className="orb dot right" src={ORB_DOT} alt=""/><img className="orb halo1" src={ORB_HALO_1} alt=""/><img className="orb halo2" src={ORB_HALO_2} alt=""/><img className="orb globe" src={ORB_GLOBE} alt=""/><img className="orb flare" src={ORB_FLARE} alt=""/><i className="tick top"/><i className="tick bottom"/></div></div>
      <div className={`figma-listening ${speaking?"is-speaking":""}`}><b>{status}</b><span><i/><i/><i/><i/></span></div>
      <div className="figma-command"><input disabled={busy} value={command} onChange={e=>setCommand(e.target.value)} onKeyDown={e=>{if(e.key==="Enter"){e.preventDefault();sendCommand()}}} placeholder="Escribe tu solicitud o comando..."/><button disabled={busy} onClick={sendCommand}>↑</button></div>
      <div className="figma-actions"><button>⌕ Analizar datos</button><button>♧ Generar informe</button><button>▦ Revisar estrategia</button><button>••• Crear contenido</button></div>
      <section className="figma-calendar"><div className="figma-section-head"><b>Calendario</b><span>Viernes, 23 de mayo</span></div>{[["09:00","Reunión de estrategia"],["11:30","Revisión de resultados"],["14:00","Presentación de proyecto"],["16:30","Análisis de mercado"]].map(([time,title],i)=><p key={time}><i className={`event-dot d${i}`}/><span>{time}</span><b>{title}</b></p>)}</section>
      <section className="figma-comms"><div className="figma-section-head"><b>Comunicaciones</b><span>▦</span></div>{[["M","María González","Actualización del proyecto Q2","22:30"],["C","Carlos Ramírez","Revisión del informe financiero","21:15"],["A","Ana López","Estrategia de marketing digital","20:50"]].map(([initial,name,desc,time],i)=><p key={name}><i className={`figma-avatar a${i}`}>{initial}</i><span><b>{name}</b><small>{desc}</small></span><time>{time}</time></p>)}</section>
      <section className="figma-agents figma-panel"><div className="figma-panel-head"><b>Agentes activos <em>5/7</em></b><span>▦</span></div><div className="figma-agent-list">{agents.map(([icon,name,desc])=><div key={name}><i>{icon}</i><span><b>{name}</b><small>{desc}</small></span><em>●</em></div>)}</div><hr/><div className="figma-agent-foot"><span>Gestionar agentes</span><b>•••</b></div></section>
    </div>}
  </div>
}
