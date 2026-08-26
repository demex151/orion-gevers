import unittest

import numpy as np

from gever.sentinel import SentinelMonitor, rms_mono, float32_to_pcm16


class FakeClap:
    def __init__(self, result=False):
        self.result = result

    def update(self, level, now):
        return self.result


class FakeWake:
    def __init__(self, available=True, result=False, flush_result=False):
        self.available = available
        self.result = result
        self.flush_result = flush_result
        self.error = None
        self.flush_calls = 0

    def feed_pcm16(self, pcm):
        return self.result

    def flush(self):
        self.flush_calls += 1
        return self.flush_result


class SentinelTests(unittest.TestCase):
    def test_rms_mono_silence(self):
        self.assertEqual(rms_mono(np.zeros((160, 1), dtype=np.float32)), 0.0)

    def test_pcm_conversion_has_expected_size(self):
        frame = np.zeros((160, 1), dtype=np.float32)
        self.assertEqual(len(float32_to_pcm16(frame)), 320)

    def test_clap_activates_without_orion(self):
        monitor = SentinelMonitor(FakeClap(True), FakeWake(result=False), stream_factory=lambda **_: None)
        activations = []
        monitor._on_activate = activations.append
        monitor._running = True
        monitor.process_frame(np.zeros((160, 1), dtype=np.float32), now=1.0)
        self.assertEqual(activations, ["clap"])

    def test_orion_activates_without_clap(self):
        wake = FakeWake(result=False, flush_result=True)
        monitor = SentinelMonitor(FakeClap(False), wake, stream_factory=lambda **_: None, voice_threshold=0.01, silence_seconds=0.25)
        activations = []
        monitor._on_activate = activations.append
        monitor._running = True
        voice = np.full((1600, 1), 0.08, dtype=np.float32)
        silence = np.zeros((1600, 1), dtype=np.float32)
        monitor.process_frame(voice, now=1.0)
        monitor.process_frame(silence, now=1.10)
        monitor.process_frame(silence, now=1.40)
        self.assertEqual(activations, ["orion"])

    def test_phrase_engine_flushes_after_voice_returns_to_silence(self):
        wake = FakeWake(result=False, flush_result=True)
        monitor = SentinelMonitor(FakeClap(False), wake, stream_factory=lambda **_: None, voice_threshold=0.01, silence_seconds=0.25)
        activations = []
        monitor._on_activate = activations.append
        monitor._running = True
        voice = np.full((1600, 1), 0.08, dtype=np.float32)
        silence = np.zeros((1600, 1), dtype=np.float32)
        monitor.process_frame(voice, now=1.0)
        monitor.process_frame(silence, now=1.10)
        monitor.process_frame(silence, now=1.40)
        self.assertEqual(wake.flush_calls, 1)
        self.assertEqual(activations, ["orion"])

    def test_degraded_wake_still_allows_clap(self):
        monitor = SentinelMonitor(FakeClap(True), FakeWake(available=False), stream_factory=lambda **_: None)
        activations = []
        monitor._on_activate = activations.append
        monitor._running = True
        monitor.process_frame(np.zeros((160, 1), dtype=np.float32), now=1.0)
        self.assertEqual(activations, ["clap"])


if __name__ == "__main__":
    unittest.main()
