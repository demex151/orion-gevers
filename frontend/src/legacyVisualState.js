const STATUS_MAP = new Map([
  ["PROCESANDO INSTRUCCIÓN", "Pensando"],
  ["PREPARANDO RESPUESTA", "Preparando voz"],
  ["ESCUCHANDO", "Escuchando"],
  ["RESPONDIENDO", "Hablando"],
  ["ESPERANDO ORION", "Escuchando"],
  ["CONEXIÓN INTERRUMPIDA", "Error de conexión"],
]);

function clean(value = "") {
  return String(value).replace(/\s+/g, " ").trim();
}

export function buildLegacyVisualSnapshot({ statusText = "", subtitleLines = [], messages = [] } = {}) {
  const normalizedStatus = clean(statusText).toUpperCase();
  const lines = (Array.isArray(subtitleLines) ? subtitleLines : [])
    .map(clean)
    .filter(Boolean);
  const subtitle = lines.at(-1) || "";

  const cleanMessages = (Array.isArray(messages) ? messages : [])
    .map((item) => ({ sender: clean(item?.sender), text: clean(item?.text) }))
    .filter((item) => item.text);

  return {
    status: STATUS_MAP.get(normalizedStatus) || (clean(statusText) || "Escuchando"),
    subtitle,
    messages: cleanMessages,
  };
}
