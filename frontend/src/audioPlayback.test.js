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
