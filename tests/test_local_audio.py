import unittest

from gever.local_audio import LocalAudioPlayer


class FakeResult:
    returncode = 0


class LocalAudioPlayerTests(unittest.TestCase):
    def test_windows_uses_powershell_media_player(self):
        calls = []

        def runner(args, **kwargs):
            calls.append((args, kwargs))
            return FakeResult()

        player = LocalAudioPlayer(platform_name="win32", runner=runner)
        result = player.play_mp3(r"C:\Temp\gever response.mp3")

        self.assertTrue(result["played"])
        self.assertEqual(result["backend"], "windows-mediaplayer")
        self.assertEqual(calls[0][0][0].lower(), "powershell")
        self.assertIn("PresentationCore", calls[0][0][5])
        self.assertIn("gever response.mp3", calls[0][0][5])

    def test_non_windows_reports_unavailable(self):
        player = LocalAudioPlayer(platform_name="linux", runner=lambda *args, **kwargs: None)
        result = player.play_mp3("/tmp/a.mp3")
        self.assertFalse(result["played"])
        self.assertEqual(result["reason"], "unsupported-platform")


if __name__ == "__main__":
    unittest.main()
