import test from "node:test";
import assert from "node:assert/strict";

import { playAudioBlob } from "./audioPlayback.js";

test("reports autoplay block without hiding the error", async () => {
  const audio = {
    play: async () => {
      const error = new Error("play() failed because the user didn't interact with the document first");
      error.name = "NotAllowedError";
      throw error;
    },
  };

  const result = await playAudioBlob(new Blob(["x"]), {
    createAudio: () => audio,
    createObjectURL: () => "blob:test",
    revokeObjectURL: () => {},
  });

  assert.equal(result.blocked, true);
  assert.equal(result.reason, "autoplay");
});

test("resolves after audio ends", async () => {
  const audio = {
    play: async () => {
      queueMicrotask(() => audio.onended?.());
    },
  };

  const result = await playAudioBlob(new Blob(["x"]), {
    createAudio: () => audio,
    createObjectURL: () => "blob:test",
    revokeObjectURL: () => {},
  });

  assert.equal(result.played, true);
  assert.equal(result.blocked, false);
});

test("aborting playback pauses audio once and resolves as interrupted", async () => {
  const abortController = new AbortController();
  let pauseCalls = 0;
  let revoked = 0;

  const audio = {
    currentTime: 12,
    play: async () => {
      queueMicrotask(() => abortController.abort());
    },
    pause: () => {
      pauseCalls += 1;
    },
  };

  const result = await playAudioBlob(new Blob(["x"]), {
    signal: abortController.signal,
    createAudio: () => audio,
    createObjectURL: () => "blob:test",
    revokeObjectURL: () => {
      revoked += 1;
    },
  });

  assert.equal(pauseCalls, 1);
  assert.equal(audio.currentTime, 0);
  assert.equal(revoked, 1);
  assert.equal(result.interrupted, true);
  assert.equal(result.played, false);
});
