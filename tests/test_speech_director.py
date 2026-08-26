import unittest

from gever.speech_director import GeversSpeechDirector


class GeversSpeechDirectorTests(unittest.TestCase):
    def setUp(self):
        self.director = GeversSpeechDirector()

    def test_keeps_short_natural_answer_intact(self):
        text = "Entendido. Ya estoy en ello."
        self.assertEqual(self.director.direct(text), text)

    def test_removes_generic_assistant_closing(self):
        text = (
            "Ya revisé el sistema. El backend está funcionando correctamente. "
            "¿Quieres que te ayude con algo más?"
        )
        spoken = self.director.direct(text)
        self.assertIn("Ya revisé el sistema.", spoken)
        self.assertNotIn("¿Quieres que te ayude con algo más?", spoken)

    def test_limits_long_spoken_answer_without_changing_numbers(self):
        text = (
            "Ya revisé el negocio. Los ingresos fueron de 128450 dólares. "
            "La retención está en 92 por ciento. Hay tres problemas importantes. "
            "El primero es la captación. El segundo es el seguimiento. "
            "El tercero es la velocidad de respuesta. Ahora conviene priorizar captación."
        )
        spoken = self.director.direct(text)
        self.assertIn("128450", spoken)
        self.assertIn("92", spoken)
        self.assertLessEqual(len(spoken.split()), 70)

    def test_does_not_invent_words(self):
        text = "Encontré un problema crítico en ORION. Debemos corregir el micrófono primero."
        spoken = self.director.direct(text)
        original_words = {word.strip(".,!?¿¡").lower() for word in text.split()}
        spoken_words = {word.strip(".,!?¿¡").lower() for word in spoken.split()}
        self.assertTrue(spoken_words.issubset(original_words))


if __name__ == "__main__":
    unittest.main()
