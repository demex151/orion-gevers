const items=data=>Array.isArray(data?.items)?data.items:[];
export function normalizePanelContent(panel={}){
 const data=panel.data??{};
 if(panel.type==="agenda")return {kind:"agenda",rows:items(data).map(x=>({primary:String(x.time??""),secondary:String(x.title??x.name??"")}))};
 if(panel.type==="leads")return {kind:"leads",rows:items(data).map(x=>({primary:String(x.name??x.title??"Oportunidad"),secondary:[x.status,x.service].filter(Boolean).join(" · ")}))};
 if(panel.type==="metrics")return {kind:"metrics",rows:items(data).map(x=>({primary:String(x.label??""),secondary:String(x.value??"")}))};
 if(panel.type==="progress")return {kind:"progress",progress:Math.max(0,Math.min(100,Number(data.value)||0)),text:String(data.label??"")};
 if(panel.type==="communications")return {kind:"communications",rows:items(data).map(x=>({primary:String(x.name??""),secondary:String(x.message??x.subject??"")}))};
 return {kind:"generic",text:String(data.text??data.message??"")};
}
