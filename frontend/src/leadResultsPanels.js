export function leadResultsPanels(payload){
 if(!payload?.run)return [];
 const r=payload.run, leads=Array.isArray(payload.leads)?payload.leads:[];
 return [
  {id:'lead-summary',title:'ÚLTIMA BÚSQUEDA',metrics:[['REVISADOS',r.raw_findings||0],['VÁLIDOS',r.accepted_leads||0],['DESCARTADOS',r.rejected_findings||0]]},
  {id:'lead-classifications',title:'CLASIFICACIÓN',metrics:[['HOT',r.hot_count||0],['WARM',r.warm_count||0],['PROSPECT',r.prospect_count||0]]},
  {id:'lead-opportunities',title:'MEJORES OPORTUNIDADES',items:leads.slice(0,5).map((x,i)=>({name:x.name||x.organization||`Oportunidad ${i+1}`,classification:x.classification||'PROSPECT',score:Number(x.score)||0,location:x.location||'Ubicación no identificada',service:x.service||x.service_requested_or_inferred||'Pintura',evidence:x.evidence||'',source_url:x.source_url||''}))}
 ];
}
