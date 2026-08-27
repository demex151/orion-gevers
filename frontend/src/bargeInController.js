export function createBargeInController(deps = {}) {
  const getUserMedia = deps.getUserMedia || ((constraints) => navigator.mediaDevices.getUserMedia(constraints));
  const createAudioContext = deps.createAudioContext || (() => new (window.AudioContext || window.webkitAudioContext)());
  const setTimer = deps.setInterval || ((fn, ms) => setInterval(fn, ms));
  const clearTimer = deps.clearInterval || ((id) => clearInterval(id));
  const rmsThreshold = deps.rmsThreshold ?? 0.055;
  const confirmationSamples = deps.confirmationSamples ?? 4;
  const sampleMs = deps.sampleMs ?? 60;

  let stream = null;
  let context = null;
  let source = null;
  let analyser = null;
  let timer = null;
  let activeSamples = 0;
  let fired = false;

  async function stop() {
    if (timer !== null) {
      clearTimer(timer);
      timer = null;
    }
    try { source?.disconnect?.(); } catch {}
    try { analyser?.disconnect?.(); } catch {}
    for (const track of stream?.getTracks?.() || []) {
      try { track.stop(); } catch {}
    }
    try { await context?.close?.(); } catch {}
    stream = null;
    context = null;
    source = null;
    analyser = null;
    activeSamples = 0;
  }

  async function start({ onSpeech }) {
    await stop();
    fired = false;
    stream = await getUserMedia({
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
      },
    });
    context = createAudioContext();
    source = context.createMediaStreamSource(stream);
    analyser = context.createAnalyser();
    analyser.fftSize = 512;
    source.connect(analyser);
    const data = new Uint8Array(analyser.fftSize);

    timer = setTimer(() => {
      if (fired || !analyser) return;
      analyser.getByteTimeDomainData(data);
      let sum = 0;
      for (let i = 0; i < data.length; i += 1) {
        const normalized = (data[i] - 128) / 128;
        sum += normalized * normalized;
      }
      const rms = Math.sqrt(sum / data.length);
      if (rms >= rmsThreshold) activeSamples += 1;
      else activeSamples = 0;
      if (activeSamples < confirmationSamples) return;
      fired = true;
      Promise.resolve(onSpeech?.()).catch((error) => console.warn("[GEVER BARGE-IN]", error));
    }, sampleMs);
  }

  return { start, stop };
}
