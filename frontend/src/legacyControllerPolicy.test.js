import test from "node:test";
import assert from "node:assert/strict";
import { shouldRunLegacyController } from "./legacyControllerPolicy.js";

test("legacy controller remains enabled for standalone App", () => {
  assert.equal(shouldRunLegacyController(undefined), true);
  assert.equal(shouldRunLegacyController(true), true);
});

test("legacy controller is disabled when HomeShell owns the session", () => {
  assert.equal(shouldRunLegacyController(false), false);
});
