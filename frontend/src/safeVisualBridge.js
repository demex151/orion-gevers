import { buildLegacyVisualSnapshot } from "./legacyVisualState.js";

const ROOT_ID = "gever-safe-visual-layer";

function readControllerState() {
  const legacy = document.querySelector(".legacy-app");
  if (!legacy) return buildLegacyVisualSnapshot();

  const statusText = legacy.querySelector(".core-status")?.textContent || "";
  const subtitleLines = Array.from(
    legacy.querySelectorAll(".core-status + div > div")
  ).map((node) => node.textContent || "");

  const messages = Array.from(
    legacy.querySelectorAll(".conversation .gever-message")
  ).map((node) => ({
    sender: node.querySelector("span")?.textContent || "",
    text: node.querySelector("p")?.textContent || "",
  }));

  return buildLegacyVisualSnapshot({ statusText, subtitleLines, messages });
}

function ensureLayer() {
  let layer = document.getElementById(ROOT_ID);
  if (layer) return layer;

  layer = document.createElement("div");
  layer.id = ROOT_ID;
  layer.innerHTML = `
    <div class="gever-safe-subtitle" aria-live="polite"></div>
    <div class="gever-safe-conversation" hidden>
      <div class="gever-safe-conversation-head">
        <strong>Conversaciones</strong>
        <button type="button" aria-label="Cerrar conversaciones">×</button>
      </div>
      <div class="gever-safe-conversation-list"></div>
    </div>
  `;
  document.body.appendChild(layer);

  layer.querySelector(".gever-safe-conversation-head button")?.addEventListener("click", () => {
    const panel = layer.querySelector(".gever-safe-conversation");
    if (panel) panel.hidden = true;
  });

  return layer;
}

function renderState() {
  const layer = ensureLayer();
  const state = readControllerState();
  const subtitle = layer.querySelector(".gever-safe-subtitle");
  const panel = layer.querySelector(".gever-safe-conversation");
  const list = layer.querySelector(".gever-safe-conversation-list");

  if (subtitle) {
    subtitle.textContent = state.subtitle;
    subtitle.dataset.visible = state.subtitle ? "true" : "false";
    subtitle.dataset.status = state.status;
  }

  if (list) {
    list.replaceChildren(
      ...state.messages.slice(-30).map((item) => {
        const row = document.createElement("div");
        row.className = `gever-safe-message ${item.sender === "TÚ" ? "is-user" : "is-gever"}`;
        const who = document.createElement("strong");
        who.textContent = item.sender || "GEVER";
        const text = document.createElement("p");
        text.textContent = item.text;
        row.append(who, text);
        return row;
      })
    );
  }

  return panel;
}

function isConversationButton(target) {
  const button = target?.closest?.(".figma-nav button");
  return Boolean(button && /conversaciones/i.test(button.textContent || ""));
}

function start() {
  ensureLayer();
  renderState();

  const legacy = document.querySelector(".legacy-app");
  if (legacy) {
    const observer = new MutationObserver(renderState);
    observer.observe(legacy, { subtree: true, childList: true, characterData: true });
  }

  document.addEventListener("click", (event) => {
    if (!isConversationButton(event.target)) return;
    event.preventDefault();
    event.stopPropagation();
    const panel = renderState();
    if (panel) panel.hidden = false;
  }, true);
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => requestAnimationFrame(start), { once: true });
} else {
  requestAnimationFrame(start);
}
