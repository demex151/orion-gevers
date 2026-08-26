export const GEVER_VISUAL_EVENT = "gever:visual-state";

export function buildVisualState({ status = "", subtitles = [], conversation = [] } = {}) {
  return {
    status: String(status || ""),
    subtitles: Array.isArray(subtitles) ? [...subtitles] : [],
    conversation: Array.isArray(conversation) ? [...conversation] : [],
  };
}

export function publishVisualState(state) {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new CustomEvent(GEVER_VISUAL_EVENT, { detail: buildVisualState(state) }));
}
