export async function playAudioBlob(blob, deps = {}) {
  const createAudio = deps.createAudio || ((url) => new Audio(url));
  const createObjectURL = deps.createObjectURL || ((value) => URL.createObjectURL(value));
  const revokeObjectURL = deps.revokeObjectURL || ((url) => URL.revokeObjectURL(url));
  const onPlaying = deps.onPlaying || (() => {});
  const signal = deps.signal;
  const url = createObjectURL(blob);
  const audio = createAudio(url);
  let settled = false;
  let interrupted = false;

  const cleanupAbort = () => signal?.removeEventListener?.("abort", onAbort);
  const onAbort = () => {
    if (settled) return;
    interrupted = true;
    try { audio.pause?.(); } catch {}
    try { audio.currentTime = 0; } catch {}
    audio.onended?.();
  };

  try {
    if (signal?.aborted) {
      onAbort();
      return { played: false, blocked: false, interrupted: true };
    }

    const ended = new Promise((resolve, reject) => {
      audio.onplaying = () => onPlaying();
      audio.onended = () => {
        settled = true;
        resolve();
      };
      audio.onerror = () => {
        settled = true;
        reject(new Error("No se pudo reproducir la voz"));
      };
      signal?.addEventListener?.("abort", onAbort, { once: true });
    });

    await audio.play();
    await ended;
    if (interrupted) return { played: false, blocked: false, interrupted: true };
    return { played: true, blocked: false, interrupted: false };
  } catch (error) {
    if (interrupted || signal?.aborted) {
      return { played: false, blocked: false, interrupted: true };
    }
    if (error?.name === "NotAllowedError") {
      return { played: false, blocked: true, reason: "autoplay", error };
    }
    throw error;
  } finally {
    settled = true;
    cleanupAbort();
    revokeObjectURL(url);
  }
}
