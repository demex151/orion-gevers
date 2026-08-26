import unittest

from gever.orion_phrase_engine import OrionPhraseEngine


class FakeRecognizer:
    def __init__(self, result=""):
        self.result = result
        self.calls = 0

    def recognize_google(self, audio, language="es-ES"):
        self.calls += 1
        return self.result


class OrionPhraseEngineTests(unittest.TestCase):
    def test_detects_orion_with_accented_transcription(self):
        engine = OrionPhraseEngine(recognizer=FakeRecognizer("orión"), min_seconds=0.01)
        pcm = b"\x01\x00" * 1600
        self.assertFalse(engine.feed_pcm16(pcm))
        self.assertTrue(engine.flush())

    def test_ignores_other_words(self):
        engine = OrionPhraseEngine(recognizer=FakeRecognizer("hola gever"), min_seconds=0.01)
        engine.feed_pcm16(b"\x01\x00" * 1600)
        self.assertFalse(engine.flush())

    def test_does_not_send_audio_until_flush(self):
        recognizer = FakeRecognizer("orion")
        engine = OrionPhraseEngine(recognizer=recognizer, min_seconds=0.01)
        self.assertFalse(engine.feed_pcm16(b"\x01\x00" * 1600))
        self.assertEqual(recognizer.calls, 0)


if __name__ == "__main__":
    unittest.main()
