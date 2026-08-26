import test from "node:test";
import assert from "node:assert/strict";
import { buildLegacyVisualSnapshot } from "./legacyVisualState.js";

test("builds current subtitle phrase and conversation from the single controller state", () => {
  const state = buildLegacyVisualSnapshot({
    statusText: "RESPONDIENDO",
    subtitleLines: ["Soy GEVER", "y estoy respondiendo."],
    messages: [
      { sender: "TÚ", text: "¿Quién eres?" },
      { sender: "GEVER", text: "Soy GEVER." },
    ],
  });

  assert.equal(state.status, "Hablando");
  assert.equal(state.subtitle, "y estoy respondiendo.");
  assert.deepEqual(state.messages, [
    { sender: "TÚ", text: "¿Quién eres?" },
    { sender: "GEVER", text: "Soy GEVER." },
  ]);
});
