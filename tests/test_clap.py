import unittest

from gever.clap import ClapDetector


class ClapDetectorTests(unittest.TestCase):
    def setUp(self):
        self.detector = ClapDetector(
            spike_ratio=7.0,
            min_rms=0.06,
            min_double_gap=0.08,
            max_double_gap=0.32,
            cooldown=0.75,
            retrigger_ratio=0.45,
            noise_floor_alpha=0.992,
            quiet_gate_mult=2.2,
        )

    def test_single_clap_does_not_activate(self):
        self.assertFalse(self.detector.update(0.001, 0.00))
        self.assertFalse(self.detector.update(0.10, 0.10))
        self.assertFalse(self.detector.update(0.001, 0.20))

    def test_two_claps_in_window_activate_once(self):
        self.detector.update(0.001, 0.00)
        self.assertFalse(self.detector.update(0.10, 0.10))
        self.detector.update(0.001, 0.18)
        self.assertTrue(self.detector.update(0.10, 0.30))
        self.assertFalse(self.detector.update(0.10, 0.31))

    def test_claps_too_far_apart_do_not_activate(self):
        self.detector.update(0.001, 0.00)
        self.assertFalse(self.detector.update(0.10, 0.10))
        self.detector.update(0.001, 0.30)
        self.assertFalse(self.detector.update(0.10, 0.60))

    def test_second_peak_requires_quiet_rearm(self):
        self.detector.update(0.001, 0.00)
        self.assertFalse(self.detector.update(0.10, 0.10))
        self.assertFalse(self.detector.update(0.09, 0.20))
        self.assertFalse(self.detector.update(0.08, 0.25))

    def test_speech_like_peaks_do_not_activate_double_clap(self):
        # Typical nearby speech can produce repeated RMS peaks around 0.02-0.05.
        # These must never arm the clap trigger.
        levels = [0.004, 0.028, 0.010, 0.041, 0.012, 0.035, 0.006]
        times = [0.00, 0.08, 0.15, 0.24, 0.31, 0.39, 0.48]
        activations = [self.detector.update(level, now) for level, now in zip(levels, times)]
        self.assertFalse(any(activations))

    def test_reset_discards_partial_clap_sequence(self):
        self.detector.update(0.001, 0.00)
        self.assertFalse(self.detector.update(0.10, 0.10))
        self.detector.reset()
        self.detector.update(0.001, 0.15)
        self.assertFalse(self.detector.update(0.10, 0.25))


if __name__ == "__main__":
    unittest.main()
