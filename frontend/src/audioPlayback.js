export async function playAudioBlob(blob, deps = {}) {
  const createAudio = deps.createAudio || ((url) => new Audio(url));
  const createObjectURL = deps.createObjectURL || ((value) => URL.createObjectURL(value));
  const revokeObjectURL = deps.revokeObjectURL || ((url) => URL.revokeObjectURL(url));
  const onPlaying = deps.onPlaying || (() => {});
  const url = createObjectURL(blob);
  const audio = createAudio(url);
  try {
    const ended = new Promise((resolve, reject) => {
      audio.onplaying = () => onPlaying();
      audio.onended = resolve;
      audio.onerror = () => reject(new Error("No se pudo reproducir la voz"));
    });
    await audio.play();
    await ended;
    return { played: true, blocked: false };
  } catch (error) {
    if (error?.name === "NotAllowedError") {
      return { played: false, blocked: true, reason: "autoplay", error };
    }
    throw error;
  } finally {
    revokeObjectURL(url);
  }
}
