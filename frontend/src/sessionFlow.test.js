import test from "node:test";
import assert from "node:assert/strict";

import { uiStateForSession } from "./sessionFlow.js";

test("sentinel does not count as conversational listening", () => {
  assert.deepEqual(uiStateForSession("SENTINEL"), {
    label: "Esperando ORION o doble aplauso",
    conversationActive: false,
  });
});

test("session enables conversational listening", () => {
  assert.deepEqual(uiStateForSession("SESSION"), {
    label: "Escuchando",
    conversationActive: true,
  });
});

test("stopped disables conversational listening", () => {
  assert.equal(uiStateForSession("STOPPED").conversationActive, false);
});
