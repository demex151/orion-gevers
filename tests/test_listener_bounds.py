import unittest
from unittest.mock import MagicMock, patch


class ListenerBoundsTests(unittest.TestCase):
    @patch("gever.listen.sr.Microphone")
    def test_conversation_listen_uses_finite_defaults(self, microphone_cls):
        microphone = MagicMock()
        source = MagicMock()
        microphone.__enter__.return_value = source
        microphone.__exit__.return_value = False
        microphone_cls.return_value = microphone

        with patch("gever.listen.sr.Recognizer") as recognizer_cls:
            recognizer = MagicMock()
            recognizer_cls.return_value = recognizer
            recognizer.listen.return_value = MagicMock()
            recognizer.recognize_google.return_value = "hola"

            from gever.listen import GeversListener
            listener = GeversListener(calibrate=False)
            self.assertEqual(listener.listen(), "hola")

            _, kwargs = recognizer.listen.call_args
            self.assertIsNotNone(kwargs["timeout"])
            self.assertIsNotNone(kwargs["phrase_time_limit"])
            self.assertGreater(kwargs["timeout"], 0)
            self.assertGreater(kwargs["phrase_time_limit"], 0)


if __name__ == "__main__":
    unittest.main()
