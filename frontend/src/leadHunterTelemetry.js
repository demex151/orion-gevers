export const PIPELINE=[['search','BUSCANDO OPORTUNIDADES'],['analyze','ANALIZANDO RESULTADOS'],['competition','DESCARTANDO COMPETENCIA'],['directories','DESCARTANDO DIRECTORIOS'],['advertising','DESCARTANDO PUBLICIDAD'],['contractors','DESCARTANDO CONTRATISTAS'],['stale','DESCARTANDO PUBLICACIONES ANTIGUAS'],['intent','DETECTANDO INTENCIÓN REAL'],['dedupe','ELIMINANDO DUPLICADOS'],['classify','CLASIFICANDO Y GUARDANDO']];
export function telemetryPanels(p){
 if(!p||p.state==='idle')return [];
 const r=p.rejections||{},c=p.classifications||{};
 return [
  {id:'lead-pipeline',title:'GEVER · LEAD HUNTER',kind:'pipeline',items:PIPELINE.map(([id,label])=>({id,label,active:p.active_stage===id,value:id==='competition'?r.competition:id==='directories'?r.directories:id==='advertising'?r.advertising:id==='contractors'?r.contractors:id==='stale'?r.stale:null}))},
  {id:'lead-counters',title:'ANÁLISIS EN TIEMPO REAL',kind:'metrics',metrics:[['Encontrados',p.found],['Analizados',p.analyzed],['Descartados',p.rejected],['Válidos',p.valid],['Duplicados',p.duplicates],['Guardados',p.saved]]},
  {id:'lead-results',title:p.state==='completed'?'RESULTADO FINAL':'OPORTUNIDADES',kind:'results',metrics:[['HOT',c.HOT||0],['WARM',c.WARM||0],['PROSPECT',c.PROSPECT||0]]}
 ];
}
