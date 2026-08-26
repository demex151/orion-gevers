import unittest

from gever.wakeword import WakeWordDetector


class WakeWordDetectorTests(unittest.TestCase):
    def test_unavailable_engine_reports_degraded_mode(self):
        detector = WakeWordDetector(
            engine_factory=lambda: (_ for _ in ()).throw(RuntimeError("missing"))
        )
        self.assertFalse(detector.available)
        self.assertIn("missing", detector.error)
        self.assertFalse(detector.feed_pcm16(b"\x00\x00" * 160))

    def test_keyword_result_activates(self):
        class FakeEngine:
            def feed_pcm16(self, pcm):
                return "orion"

        detector = WakeWordDetector(engine_factory=lambda keyword: FakeEngine())
        self.assertTrue(detector.available)
        self.assertTrue(detector.feed_pcm16(b"\x00\x00" * 160))

    def test_non_orion_hypothesis_does_not_activate(self):
        class FakeEngine:
            def feed_pcm16(self, pcm):
                return "hola"

        detector = WakeWordDetector(engine_factory=lambda keyword: FakeEngine())
        self.assertFalse(detector.feed_pcm16(b"\x00\x00" * 160))

    def test_boolean_engine_result_is_supported(self):
        class FakeEngine:
            def feed_pcm16(self, pcm):
                return True

        detector = WakeWordDetector(engine_factory=lambda keyword: FakeEngine())
        self.assertTrue(detector.feed_pcm16(b"\x00\x00" * 160))


if __name__ == "__main__":
    unittest.main()
