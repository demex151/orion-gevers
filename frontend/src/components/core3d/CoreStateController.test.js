import test from "node:test";
import assert from "node:assert/strict";
import { getCoreMotionProfile } from "./CoreStateController.js";

test("idle is the calmest profile", () => {
  const idle = getCoreMotionProfile("idle");
  const thinking = getCoreMotionProfile("thinking");
  assert.ok(idle.rotationSpeed < thinking.rotationSpeed);
  assert.ok(idle.particleEnergy < thinking.particleEnergy);
});

test("thinking and working increase orbital activity", () => {
  const idle = getCoreMotionProfile("idle");
  assert.ok(getCoreMotionProfile("thinking").orbitSpeed > idle.orbitSpeed);
  assert.ok(getCoreMotionProfile("working").orbitSpeed > idle.orbitSpeed);
});

test("speaking has the strongest pulse", () => {
  const speaking = getCoreMotionProfile("speaking");
  for (const state of ["idle", "listening", "thinking", "working", "error"]) {
    assert.ok(speaking.pulse >= getCoreMotionProfile(state).pulse);
  }
});

test("error profile is deterministic", () => {
  assert.deepEqual(getCoreMotionProfile("error"), getCoreMotionProfile("error"));
  assert.equal(getCoreMotionProfile("unknown").state, "idle");
});
