export default function CommandBar({ value = "", onChange, onSubmit, busy = false }) {
  function handleKeyDown(event) {
    if (event.key === "Enter") {
      event.preventDefault();
      onSubmit?.();
    }
  }

  return <div className="hud-command-wrap">
    <div className="hud-command-scan" />
    <div className="hud-command">
      <span className="command-prefix">›</span>
      <input aria-label="Comando para GEVER" disabled={busy} value={value} onChange={(event) => onChange?.(event.target.value)} onKeyDown={handleKeyDown} placeholder={busy ? "GEVER está procesando..." : "Escribe tu solicitud o comando..."} />
      <button disabled={busy || !value.trim()} onClick={() => onSubmit?.()} aria-label="Enviar comando">↑</button>
    </div>
  </div>;
}
