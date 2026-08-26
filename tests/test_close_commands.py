import unittest

from gever.commands import is_close_session_command


class CloseCommandTests(unittest.TestCase):
    def test_natural_spanish_close_phrases(self):
        phrases = [
            "cierra la sesión",
            "cerremos la sesión",
            "cierra el chat",
            "terminemos",
            "terminemos por ahora",
            "hasta aquí",
            "deja de escuchar",
            "para de escuchar",
            "finaliza la conversación",
        ]
        for phrase in phrases:
            with self.subTest(phrase=phrase):
                self.assertTrue(is_close_session_command(phrase))

    def test_normal_work_request_does_not_close(self):
        self.assertFalse(is_close_session_command("terminemos el presupuesto mañana"))
        self.assertFalse(is_close_session_command("cierra la ventana del navegador"))
        self.assertFalse(is_close_session_command("hasta aquí llega el reporte, continúa mañana"))


if __name__ == "__main__":
    unittest.main()
