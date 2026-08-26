import test from "node:test";
import assert from "node:assert/strict";
import { buildVisualState } from "./geverVisualBridge.js";

test("visual bridge preserves voice state without controlling audio", () => {
  const state = buildVisualState({
    status: "HABLANDO",
    subtitles: ["Soy GEVER", "y estoy respondiendo."],
    conversation: [{ sender: "GEVER", text: "Hola" }],
  });
  assert.equal(state.status, "HABLANDO");
  assert.deepEqual(state.subtitles, ["Soy GEVER", "y estoy respondiendo."]);
  assert.equal(state.conversation[0].sender, "GEVER");
});
