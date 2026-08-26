import unittest

from gever.wakeword import WakeWordDetector


class WakeWordDetectorTests(unittest.TestCase):
    def test_unavailable_engine_reports_degraded_mode(self):
        detector = WakeWordDetector(
            decoder_factory=lambda: (_ for _ in ()).throw(RuntimeError("missing"))
        )
        self.assertFalse(detector.available)
        self.assertIn("missing", detector.error)
        self.assertFalse(detector.feed_pcm16(b"\x00\x00" * 160))

    def test_keyword_result_activates(self):
        class FakeDecoder:
            def process_raw(self, pcm, no_search, full_utt):
                return None

            def hyp(self):
                return type("Hyp", (), {"hypstr": "orion"})()

        detector = WakeWordDetector(decoder_factory=lambda: FakeDecoder())
        self.assertTrue(detector.available)
        self.assertTrue(detector.feed_pcm16(b"\x00\x00" * 160))

    def test_non_orion_hypothesis_does_not_activate(self):
        class FakeDecoder:
            def process_raw(self, pcm, no_search, full_utt):
                return None

            def hyp(self):
                return type("Hyp", (), {"hypstr": "hola"})()

        detector = WakeWordDetector(decoder_factory=lambda: FakeDecoder())
        self.assertFalse(detector.feed_pcm16(b"\x00\x00" * 160))


if __name__ == "__main__":
    unittest.main()
