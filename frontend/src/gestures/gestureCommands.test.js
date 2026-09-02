import test from "node:test";
import assert from "node:assert/strict";
import { normalizeGestureCommand } from "./gestureCommands.js";

test("rejects unsupported gesture commands", () => {
  assert.equal(normalizeGestureCommand({ type: "explode" }), null);
});

test("normalizes rotate and zoom values", () => {
  assert.deepEqual(normalizeGestureCommand({ type: "rotate", value: { x: 1, y: -2 } }), { type: "rotate", value: { x: 1, y: -2 } });
  assert.deepEqual(normalizeGestureCommand({ type: "zoom", value: 1.4 }), { type: "zoom", value: 1.4 });
});

test("supports panel and reset commands", () => {
  for (const type of ["select", "open-panel", "close-panel", "reset-view"]) {
    assert.equal(normalizeGestureCommand({ type })?.type, type);
  }
});
