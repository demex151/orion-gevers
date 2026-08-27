import test from "node:test";
import assert from "node:assert/strict";

import { playSpeechWithBargeIn } from "./speechPlayback.js";

test("stops GEVER audio immediately when user speech is detected", async () => {
  let paused = 0;
  let detectorStopped = 0;
  let onSpeech;

  const audio = {
    currentTime: 0,
    onplaying: null,
    onended: null,
    onerror: null,
    play() {
      this.onplaying?.();
      return Promise.resolve();
    },
    pause() { paused += 1; },
  };

  const detector = {
    async start(options) { onSpeech = options.onSpeech; },
    async stop() { detectorStopped += 1; },
  };

  const playback = playSpeechWithBargeIn({
    audio,
    detector,
    onPlaying: () => {},
  });

  await Promise.resolve();
  await onSpeech();
  const result = await playback;

  assert.equal(paused, 1);
  assert.equal(audio.currentTime, 0);
  assert.equal(result.interrupted, true);
  assert.ok(detectorStopped >= 1);
});

test("normal audio completion does not report an interruption", async () => {
  let onSpeech;
  const audio = {
    currentTime: 0,
    onplaying: null,
    onended: null,
    onerror: null,
    play() {
      this.onplaying?.();
      queueMicrotask(() => this.onended?.());
      return Promise.resolve();
    },
    pause() { throw new Error("normal completion must not pause audio"); },
  };
  const detector = {
    async start(options) { onSpeech = options.onSpeech; },
    async stop() {},
  };

  const result = await playSpeechWithBargeIn({ audio, detector, onPlaying: () => {} });

  assert.equal(typeof onSpeech, "function");
  assert.equal(result.interrupted, false);
});
