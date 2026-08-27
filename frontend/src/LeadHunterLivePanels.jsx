import {useEffect,useState} from 'react';
import {telemetryPanels} from './leadHunterTelemetry.js';
import './LeadHunterLivePanels.css';
export default function LeadHunterLivePanels(){
 const [progress,setProgress]=useState(null);
 useEffect(()=>{let alive=true,timer; const poll=async()=>{try{const r=await fetch('http://127.0.0.1:8000/api/lead-hunter/progress');const j=await r.json();if(alive&&j.ok)setProgress(j.progress)}catch{};if(alive)timer=setTimeout(poll,350)};poll();return()=>{alive=false;clearTimeout(timer)}},[]);
 const panels=telemetryPanels(progress);if(!panels.length)return null;
 return <div className="lh-live">
  <section className="lh-panel lh-pipeline"><h3>{panels[0].title}</h3>{panels[0].items.map((x,i)=><div className={'lh-stage '+(x.active?'active':'')} key={x.id}><span>{String(i+1).padStart(2,'0')}</span><b>{x.label}</b>{x.value!=null&&<em>{x.value}</em>}</div>)}</section>
  <section className="lh-panel lh-counts"><h3>{panels[1].title}</h3><div className="lh-grid">{panels[1].metrics.map(([k,v])=><div key={k}><strong>{v||0}</strong><span>{k}</span><i style={{width:`${Math.min(100,(v||0)*8)}%`}}/></div>)}</div></section>
  <section className="lh-panel lh-results"><h3>{panels[2].title}</h3>{panels[2].metrics.map(([k,v])=><div className="lh-result" key={k}><b>{k}</b><strong>{v}</strong><i style={{width:`${Math.min(100,(v||0)*20)}%`}}/></div>)}</section>
 </div>
}
