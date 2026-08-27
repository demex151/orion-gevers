from gever.listen import GeversListener


def test_listen_uses_finite_defaults_when_limits_are_omitted():
    listener = GeversListener.__new__(GeversListener)

    class FakeMicrophone:
        def __enter__(self):
            return "source"

        def __exit__(self, exc_type, exc, tb):
            return False

    class FakeRecognizer:
        def __init__(self):
            self.call = None

        def listen(self, source, timeout=None, phrase_time_limit=None):
            self.call = (source, timeout, phrase_time_limit)
            return "audio"

    listener.microphone = FakeMicrophone()
    listener.recognizer = FakeRecognizer()
    listener.recognize_audio = lambda audio: "hola"

    assert listener.listen() == "hola"
    assert listener.recognizer.call == ("source", 8, 15)


def test_explicit_listener_limits_are_preserved():
    listener = GeversListener.__new__(GeversListener)

    class FakeMicrophone:
        def __enter__(self):
            return "source"

        def __exit__(self, exc_type, exc, tb):
            return False

    class FakeRecognizer:
        def __init__(self):
            self.call = None

        def listen(self, source, timeout=None, phrase_time_limit=None):
            self.call = (source, timeout, phrase_time_limit)
            return "audio"

    listener.microphone = FakeMicrophone()
    listener.recognizer = FakeRecognizer()
    listener.recognize_audio = lambda audio: "hola"

    assert listener.listen(timeout=3, phrase_time_limit=7) == "hola"
    assert listener.recognizer.call == ("source", 3, 7)
