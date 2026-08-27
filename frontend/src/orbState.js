export function normalizeOrbState(status){
 const value=String(status??"").toUpperCase();
 if(value.includes("ESCUCH")||value.includes("LISTEN"))return "listening";
 if(value.includes("PENS")||value.includes("PREPARANDO")||value.includes("PROCESS"))return "thinking";
 if(value.includes("HABLANDO")||value.includes("SPEAK"))return "speaking";
 if(value.includes("EJECUT")||value.includes("WORK"))return "working";
 return "idle";
}
export function orbClassName(status){return `is-${normalizeOrbState(status)}`;}
