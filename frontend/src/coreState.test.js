import test from "node:test";
import assert from "node:assert/strict";
import { normalizeCoreState } from "./coreState.js";

const cases = [
  ["", "idle"],
  ["ESPERANDO ORION", "idle"],
  ["Escuchando", "listening"],
  ["PENSANDO", "thinking"],
  ["Hablando", "speaking"],
  ["Procesando información", "working"],
  ["TRABAJANDO", "working"],
  ["Error de conexión", "error"],
];

for (const [input, expected] of cases) {
  test(`normalizeCoreState(${JSON.stringify(input)}) -> ${expected}`, () => {
    assert.equal(normalizeCoreState(input), expected);
  });
}

test("normalizeCoreState is accent tolerant", () => {
  assert.equal(normalizeCoreState("Escuchándote"), "listening");
});
