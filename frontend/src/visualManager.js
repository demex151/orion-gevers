const SAFE_SLOTS=["upper-right","lower-left","lower-right"];

export function createVisualState(){return {panels:[]};}

function normalizeSlots(panels){
  return panels.map((panel,index)=>({...panel,slot:SAFE_SLOTS[index]}));
}

export function openPanel(state,panel){
  const current=state?.panels??[];
  const existing=current.find(item=>item.id===panel.id);
  let next=current.filter(item=>item.id!==panel.id);
  const merged={...(existing??{}),...panel,minimized:false};
  next=[...next,merged];
  if(next.length>SAFE_SLOTS.length)next=next.slice(next.length-SAFE_SLOTS.length);
  return {panels:normalizeSlots(next)};
}

export function updatePanel(state,id,patch){
  return {panels:(state?.panels??[]).map(panel=>panel.id===id?{...panel,...patch,id:panel.id}:panel)};
}

export function minimizePanel(state,id){return updatePanel(state,id,{minimized:true});}

export function closePanel(state,id){return {panels:normalizeSlots((state?.panels??[]).filter(panel=>panel.id!==id))};}

export function closeAllPanels(){return createVisualState();}
