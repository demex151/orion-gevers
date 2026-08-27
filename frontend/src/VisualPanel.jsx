import {normalizePanelContent} from "./visualPanelModel.js";
import "./VisualPanel.css";
export default function VisualPanel({panel}){
 const model=normalizePanelContent(panel);
 return <section className={`gever-visual-panel slot-${panel.slot}${panel.minimized?" is-minimized":""}`} data-panel-type={panel.type}>
  <header><span>{panel.title||"GEVER"}</span><i>●</i></header>
  {!panel.minimized&&<div className="gever-panel-body">
   {model.rows?.map((row,i)=><div className="gever-panel-row" key={`${row.primary}-${i}`}><b>{row.primary}</b><small>{row.secondary}</small></div>)}
   {model.kind==="progress"&&<><div className="gever-progress"><i style={{width:`${model.progress}%`}}/></div><small>{model.text}</small></>}
   {model.kind==="generic"&&<p>{model.text}</p>}
  </div>}
 </section>
}
