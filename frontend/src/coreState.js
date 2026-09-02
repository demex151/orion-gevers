export function normalizeCoreState(status = "") {
  const normalized = String(status || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .trim();

  if (!normalized || normalized.includes("esperando") || normalized.includes("idle")) return "idle";
  if (normalized.includes("error") || normalized.includes("fallo") || normalized.includes("offline")) return "error";
  if (normalized.includes("escuch")) return "listening";
  if (normalized.includes("pens")) return "thinking";
  if (normalized.includes("habl") || normalized.includes("respond")) return "speaking";
  if (normalized.includes("proces") || normalized.includes("trabaj") || normalized.includes("ejecut")) return "working";
  return "idle";
}
