import test from "node:test";
import assert from "node:assert/strict";
import { buildLegacyVisualSnapshot } from "./legacyVisualState.js";

test("builds subtitles and conversation from the single legacy controller state", () => {
  const state = buildLegacyVisualSnapshot({
    statusText: "RESPONDIENDO",
    subtitleLines: ["Soy GEVER", "y estoy respondiendo."],
    messages: [
      { sender: "TÚ", text: "¿Quién eres?" },
      { sender: "GEVER", text: "Soy GEVER." },
    ],
  });

  assert.equal(state.status, "Hablando");
  assert.equal(state.subtitle, "Soy GEVER y estoy respondiendo.");
  assert.deepEqual(state.messages, [
    { sender: "TÚ", text: "¿Quién eres?" },
    { sender: "GEVER", text: "Soy GEVER." },
  ]);
});
