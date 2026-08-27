export function playSpeechWithBargeIn({ audio, detector, onPlaying }) {
  let settled = false;
  let interrupted = false;

  return new Promise((resolve, reject) => {
    async function finish(result) {
      if (settled) return;
      settled = true;
      try {
        await detector?.stop?.();
      } catch {}
      resolve(result);
    }

    audio.onplaying = async () => {
      onPlaying?.();
      try {
        await detector?.start?.({
          onSpeech: async () => {
            if (settled) return;
            interrupted = true;
            try { audio.pause?.(); } catch {}
            try { audio.currentTime = 0; } catch {}
            await finish({ interrupted: true });
          },
        });
      } catch {
        // If barge-in is unavailable, let playback continue normally.
      }
    };

    audio.onended = () => {
      finish({ interrupted });
    };

    audio.onerror = async () => {
      if (settled) return;
      settled = true;
      try {
        await detector?.stop?.();
      } catch {}
      reject(new Error("No se pudo reproducir la voz"));
    };

    Promise.resolve(audio.play()).catch(async (error) => {
      if (settled) return;
      settled = true;
      try {
        await detector?.stop?.();
      } catch {}
      reject(error);
    });
  });
}
