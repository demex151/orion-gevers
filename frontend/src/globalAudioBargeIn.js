import { createBargeInController } from "./bargeInController.js";

export function installGlobalAudioBargeIn({
  AudioClass = globalThis.Audio,
  createDetector = createBargeInController,
  EventClass = globalThis.Event,
} = {}) {
  if (!AudioClass?.prototype?.play || AudioClass.prototype.__geverBargeInInstalled) {
    return () => {};
  }

  const prototype = AudioClass.prototype;
  const originalPlay = prototype.play;
  prototype.__geverBargeInInstalled = true;

  prototype.play = function geverInterruptiblePlay(...args) {
    const audio = this;
    const detector = createDetector();
    let settled = false;

    const stopDetector = async () => {
      try { await detector?.stop?.(); } catch {}
    };

    const cleanup = () => { void stopDetector(); };
    audio.addEventListener?.("ended", cleanup, { once: true });
    audio.addEventListener?.("error", cleanup, { once: true });

    const result = originalPlay.apply(audio, args);

    Promise.resolve(result).then(async () => {
      try {
        await detector?.start?.({
          onSpeech: async () => {
            if (settled) return;
            settled = true;
            try { audio.pause?.(); } catch {}
            try { audio.currentTime = 0; } catch {}
            await stopDetector();
            try { audio.dispatchEvent?.(new EventClass("ended")); } catch {}
          },
        });
      } catch (error) {
        console.warn("[GEVER BARGE-IN] Detector no disponible; continúa la voz normal", error);
      }
    }).catch(cleanup);

    return result;
  };

  return () => {
    prototype.play = originalPlay;
    delete prototype.__geverBargeInInstalled;
  };
}

if (typeof globalThis.Audio !== "undefined") {
  installGlobalAudioBargeIn();
}
