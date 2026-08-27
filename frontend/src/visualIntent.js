function normalize(text){return String(text??"").normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase();}
export function inferVisualIntent(text){
 const value=normalize(text);
 if(/\b(cierra|cerrar|oculta|quitar?)\b.*\b(panel|paneles|ventana|ventanas)\b/.test(value))return {action:"close-all"};
 if(/\b(agenda|calendario|citas|reuniones)\b/.test(value))return {action:"open",type:"agenda"};
 if(/\b(leads?|clientes?|oportunidades?)\b/.test(value)&&/\b(muestra|muestrame|revisa|encontraste|encontrados?|nuevos?)\b/.test(value))return {action:"open",type:"leads"};
 if(/\b(metricas?|estadisticas?|grafic[ao]s?|resultados?)\b/.test(value))return {action:"open",type:"metrics"};
 if(/\b(progreso|avance|como va|estado de la tarea)\b/.test(value))return {action:"open",type:"progress"};
 return null;
}
