import test from "node:test";
import assert from "node:assert/strict";
import { installGlobalAudioBargeIn } from "./globalAudioBargeIn.js";

test("pauses legacy Audio and emits ended when user speaks", async () => {
  let speechHandler;
  let pauseCalls = 0;
  let endedCalls = 0;

  class FakeAudio {
    constructor() { this.currentTime = 4; }
    async play() { return "playing"; }
    pause() { pauseCalls += 1; }
    dispatchEvent(event) { if (event.type === "ended") endedCalls += 1; }
  }

  const detector = {
    async start({ onSpeech }) { speechHandler = onSpeech; },
    async stop() {},
  };

  const restore = installGlobalAudioBargeIn({
    AudioClass: FakeAudio,
    createDetector: () => detector,
    EventClass: class { constructor(type) { this.type = type; } },
  });

  const audio = new FakeAudio();
  await audio.play();
  await speechHandler();

  assert.equal(pauseCalls, 1);
  assert.equal(audio.currentTime, 0);
  assert.equal(endedCalls, 1);
  restore();
});
