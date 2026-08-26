import threading
import time

import numpy as np


def rms_mono(frame) -> float:
    samples = np.asarray(frame, dtype=np.float32).reshape(-1)
    if samples.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(samples), dtype=np.float64)))


def float32_to_pcm16(frame) -> bytes:
    samples = np.asarray(frame, dtype=np.float32).reshape(-1)
    clipped = np.clip(samples, -1.0, 1.0)
    return (clipped * 32767.0).astype(np.int16).tobytes()


class SentinelMonitor:
    """Own the microphone only while GEVER is idle.

    Frames are inspected locally for clap energy and the ORION keyword.
    This component has no dependency on GEVER's brain, chat, memory or TTS.
    """

    def __init__(
        self,
        clap_detector,
        wake_detector,
        *,
        samplerate=16000,
        blocksize=1600,
        device=None,
        stream_factory=None,
    ):
        self.clap_detector = clap_detector
        self.wake_detector = wake_detector
        self.samplerate = samplerate
        self.blocksize = blocksize
        self.device = device
        self._stream_factory = stream_factory
        self._stream = None
        self._running = False
        self._activation_sent = False
        self._on_activate = None
        self._lock = threading.RLock()
        self.error = None

    def _default_stream_factory(self, **kwargs):
        import sounddevice as sd
        return sd.InputStream(**kwargs)

    def start(self, on_activate):
        with self._lock:
            if self._running:
                return
            self._on_activate = on_activate
            self._activation_sent = False
            self.error = None
            factory = self._stream_factory or self._default_stream_factory
            try:
                self._stream = factory(
                    samplerate=self.samplerate,
                    blocksize=self.blocksize,
                    channels=1,
                    dtype="float32",
                    device=self.device,
                    callback=self._audio_callback,
                )
                self._stream.start()
                self._running = True
            except Exception as exc:
                self.error = str(exc)
                self._stream = None
                self._running = False

    def stop(self):
        with self._lock:
            self._running = False
            stream = self._stream
            self._stream = None
            if stream is not None:
                try:
                    stream.stop()
                finally:
                    stream.close()

    def _audio_callback(self, indata, frames, time_info, status):
        if status:
            self.error = str(status)
        self.process_frame(indata, now=time.monotonic())

    def process_frame(self, frame, now=None):
        with self._lock:
            if not self._running or self._activation_sent:
                return None
            now = time.monotonic() if now is None else now
            level = rms_mono(frame)
            if self.clap_detector.update(level, now):
                return self._emit_activation("clap")
            if self.wake_detector.available and self.wake_detector.feed_pcm16(float32_to_pcm16(frame)):
                return self._emit_activation("orion")
            return None

    def _emit_activation(self, trigger):
        self._activation_sent = True
        callback = self._on_activate
        if callback is not None:
            callback(trigger)
        return trigger

    def snapshot(self):
        return {
            "running": self._running,
            "error": self.error,
            "orion_available": bool(self.wake_detector.available),
            "orion_error": self.wake_detector.error,
        }
