export const GEVER_GESTURE_EVENT = "gever:gesture-command";
const SUPPORTED = new Set(["rotate", "zoom", "select", "open-panel", "close-panel", "reset-view"]);

export function normalizeGestureCommand(command = {}) {
  const type = String(command.type || "").trim();
  if (!SUPPORTED.has(type)) return null;
  if (type === "rotate") {
    const x = Number(command.value?.x ?? 0);
    const y = Number(command.value?.y ?? 0);
    if (!Number.isFinite(x) || !Number.isFinite(y)) return null;
    return { type, value: { x, y } };
  }
  if (type === "zoom") {
    const value = Number(command.value ?? 1);
    if (!Number.isFinite(value)) return null;
    return { type, value: Math.min(2.4, Math.max(0.55, value)) };
  }
  return { type, ...(command.value === undefined ? {} : { value: command.value }) };
}

export function publishGestureCommand(command) {
  const normalized = normalizeGestureCommand(command);
  if (!normalized || typeof window === "undefined") return false;
  window.dispatchEvent(new CustomEvent(GEVER_GESTURE_EVENT, { detail: normalized }));
  return true;
}
