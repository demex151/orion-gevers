const LABELS = { idle: "EN ESPERA", listening: "ESCUCHANDO", thinking: "PENSANDO", speaking: "HABLANDO", working: "TRABAJANDO", error: "ERROR" };

export default function SystemFooter({ coreState = "idle", status = "" }) {
  return <footer className="gever-system-footer">
    <div><span className={`footer-state state-${coreState}`}>● {LABELS[coreState] ?? "EN ESPERA"}</span><small>{status}</small></div>
    <div className="footer-signals"><span>◫ RED LOCAL</span><span>◉ VOZ</span><span>◇ MEMORIA</span><span>GEVER v0.3</span></div>
  </footer>;
}
