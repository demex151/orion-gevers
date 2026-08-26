export function uiStateForSession(state) {
  switch (state) {
    case "SESSION":
      return { label: "Escuchando", conversationActive: true };
    case "SENTINEL":
      return {
        label: "Esperando ORION o doble aplauso",
        conversationActive: false,
      };
    case "STOPPED":
    default:
      return { label: "Detenido", conversationActive: false };
  }
}
