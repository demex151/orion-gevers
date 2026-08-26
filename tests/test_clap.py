import unittest

from gever.clap import ClapDetector


class ClapDetectorTests(unittest.TestCase):
    def setUp(self):
        self.detector = ClapDetector(
            spike_ratio=7.0,
            min_rms=0.012,
            min_double_gap=0.05,
            max_double_gap=0.35,
            cooldown=0.45,
            retrigger_ratio=0.55,
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


if __name__ == "__main__":
    unittest.main()
