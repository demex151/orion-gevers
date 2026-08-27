export function nextPanelVisibility(state,runtimeState){
 const next={...state};
 if(runtimeState==='speaking'){next.sawSpeaking=true;return next;}
 if(next.visible&&next.sawSpeaking&&runtimeState!=='speaking')next.visible=false;
 return next;
}

export function currentGeverRuntimeState(){
 const orb=document.querySelector('.figma-orb-visualizer');
 return orb?.dataset?.geverState||'idle';
}
