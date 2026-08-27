export const ORB_RUNTIME_EVENT="gever:runtime-status";
export function createOrbRuntimeBridge(target=globalThis){
 return {
  publish(status){
   if(!target?.dispatchEvent)return;
   const EventCtor=globalThis.CustomEvent??class{constructor(type,init){this.type=type;this.detail=init?.detail}};
   target.dispatchEvent(new EventCtor(ORB_RUNTIME_EVENT,{detail:{status:String(status??"ESPERANDO")}}));
  }
 };
}
export function subscribeOrbRuntime(listener,target=globalThis){
 if(!target?.addEventListener)return()=>{};
 const handler=event=>listener(event?.detail?.status??"ESPERANDO");
 target.addEventListener(ORB_RUNTIME_EVENT,handler);
 return()=>target.removeEventListener?.(ORB_RUNTIME_EVENT,handler);
}
