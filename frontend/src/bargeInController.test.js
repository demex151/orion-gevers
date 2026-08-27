import test from "node:test";
import assert from "node:assert/strict";

import { createBargeInController } from "./bargeInController.js";

test("requests echo protected microphone audio and releases resources", async () => {
  let constraints;
  let stopped = 0;
  let closed = 0;
  const track = { stop: () => { stopped += 1; } };
  const stream = { getTracks: () => [track] };
  const analyser = { fftSize: 0, getByteTimeDomainData: (data) => data.fill(128), disconnect: () => {} };
  const source = { connect: () => {}, disconnect: () => {} };
  const context = {
    createMediaStreamSource: () => source,
    createAnalyser: () => analyser,
    close: async () => { closed += 1; },
  };
  const controller = createBargeInController({
    getUserMedia: async (value) => { constraints = value; return stream; },
    createAudioContext: () => context,
    setInterval: () => 1,
    clearInterval: () => {},
  });

  await controller.start({ onSpeech: () => {} });
  await controller.stop();

  assert.deepEqual(constraints, { audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true } });
  assert.equal(stopped, 1);
  assert.equal(closed, 1);
});

test("requires sustained activity and fires only once", async () => {
  let sample;
  let calls = 0;
  const stream = { getTracks: () => [{ stop: () => {} }] };
  const analyser = {
    fftSize: 0,
    getByteTimeDomainData(data) {
      data.fill(128);
      if (sample === "voice") data[0] = 255;
    },
    disconnect: () => {},
  };
  const context = {
    createMediaStreamSource: () => ({ connect: () => {}, disconnect: () => {} }),
    createAnalyser: () => analyser,
    close: async () => {},
  };
  let tick;
  const controller = createBargeInController({
    getUserMedia: async () => stream,
    createAudioContext: () => context,
    setInterval: (fn) => { tick = fn; return 1; },
    clearInterval: () => {},
    confirmationSamples: 3,
    rmsThreshold: 0.05,
  });

  await controller.start({ onSpeech: () => { calls += 1; } });
  sample = "voice";
  tick();
  sample = "quiet";
  tick();
  assert.equal(calls, 0);
  sample = "voice";
  tick(); tick(); tick(); tick();
  assert.equal(calls, 1);
  await controller.stop();
});
