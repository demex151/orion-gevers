import {useEffect,useRef,useState} from 'react';
import {telemetryPanels} from './leadHunterTelemetry.js';
import {leadResultsPanels} from './leadResultsPanels.js';
import './LeadHunterLivePanels.css';

function StoredResults({payload}){const panels=leadResultsPanels(payload);if(!panels.length)return null;return <div className="lh-live lh-summary-mode">
 <section className="lh-panel lh-pipeline"><h3>{panels[0].title}</h3><div className="lh-grid">{panels[0].metrics.map(([k,v])=><div key={k}><strong>{v}</strong><span>{k}</span><i style={{width:`${Math.min(100,(v||0)*4)}%`}}/></div>)}</div></section>
 <section className="lh-panel lh-counts"><h3>{panels[1].title}</h3>{panels[1].metrics.map(([k,v])=><div className="lh-result" key={k}><b>{k}</b><strong>{v}</strong><i style={{width:`${Math.min(100,(v||0)*25)}%`}}/></div>)}</section>
 <section className="lh-panel lh-results lh-opportunities"><h3>{panels[2].title}</h3>{panels[2].items.length?panels[2].items.map((x,i)=><article className="lh-lead" key={i}><header><b>{x.name}</b><span>{x.classification} · {x.score}</span></header><small>{x.location} · {x.service}</small><p>{x.evidence}</p>{x.source_url&&<em>{new URL(x.source_url).hostname}</em>}</article>):<p className="lh-empty">No hay oportunidades guardadas.</p>}</section>
 </div>}

export default function LeadHunterLivePanels(){
 const [progress,setProgress]=useState(null),[results,setResults]=useState(null),[showResults,setShowResults]=useState(false);const lastState=useRef('idle');
 useEffect(()=>{let alive=true,timer;const poll=async()=>{try{const r=await fetch('http://127.0.0.1:8000/api/lead-hunter/progress'),j=await r.json();if(alive&&j.ok){setProgress(j.progress);if(j.progress?.state==='completed'&&lastState.current!=='completed'){const rr=await fetch('http://127.0.0.1:8000/api/lead-hunter/results'),rj=await rr.json();if(alive&&rj.ok){setResults(rj);setShowResults(true);setTimeout(()=>alive&&setShowResults(false),15000)}}lastState.current=j.progress?.state||'idle'}}catch{}if(alive)timer=setTimeout(poll,350)};poll();return()=>{alive=false;clearTimeout(timer)}},[]);
 if(showResults&&results)return <StoredResults payload={results}/>;
 const panels=telemetryPanels(progress);if(!panels.length)return null;
 return <div className="lh-live"><section className="lh-panel lh-pipeline"><h3>{panels[0].title}</h3>{panels[0].items.map((x,i)=><div className={'lh-stage '+(x.active?'active':'')} key={x.id}><span>{String(i+1).padStart(2,'0')}</span><b>{x.label}</b>{x.value!=null&&<em>{x.value}</em>}</div>)}</section><section className="lh-panel lh-counts"><h3>{panels[1].title}</h3><div className="lh-grid">{panels[1].metrics.map(([k,v])=><div key={k}><strong>{v||0}</strong><span>{k}</span><i style={{width:`${Math.min(100,(v||0)*8)}%`}}/></div>)}</div></section><section className="lh-panel lh-results"><h3>{panels[2].title}</h3>{panels[2].metrics.map(([k,v])=><div className="lh-result" key={k}><b>{k}</b><strong>{v}</strong><i style={{width:`${Math.min(100,(v||0)*20)}%`}}/></div>)}</section></div>
}
