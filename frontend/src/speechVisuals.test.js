import test from "node:test";
import assert from "node:assert/strict";
import { createSubtitleChunks, subtitleAtTime } from "./speechVisuals.js";

test("splits long GEVER speech into readable subtitle chunks", () => {
  const chunks = createSubtitleChunks(
    "GEVER puede analizar datos y también ayudarte a tomar mejores decisiones para tu negocio todos los días."
  );

  assert.ok(chunks.length >= 2);
  assert.ok(chunks.every((chunk) => chunk.length <= 58));
});

test("selects the current subtitle from audio progress", () => {
  const chunks = ["uno", "dos", "tres"];

  assert.equal(subtitleAtTime(chunks, 0, 9), "uno");
  assert.equal(subtitleAtTime(chunks, 4, 9), "dos");
  assert.equal(subtitleAtTime(chunks, 8.9, 9), "tres");
});
