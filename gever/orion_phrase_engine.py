import unicodedata

import speech_recognition as sr


def _normalize(text):
    text = unicodedata.normalize("NFD", str(text or "").lower())
    return "".join(ch for ch in text if unicodedata.category(ch) != "Mn")


class OrionPhraseEngine:
    """Small ORION phrase recognizer without PocketSphinx native binaries.

    PCM is accumulated by the sentinel and recognition happens only when
    flush() is called after an utterance boundary. This reuses the project's
    existing SpeechRecognition dependency and avoids the blocked .pyd file.
    """

    def __init__(self, keyword="orion", recognizer=None, sample_rate=16000, min_seconds=0.20):
        self.keyword = _normalize(keyword).strip()
        self.recognizer = recognizer or sr.Recognizer()
        self.sample_rate = int(sample_rate)
        self.min_bytes = int(self.sample_rate * 2 * float(min_seconds))
        self._buffer = bytearray()

    def feed_pcm16(self, pcm):
        if pcm:
            self._buffer.extend(pcm)
        return False

    def flush(self):
        if len(self._buffer) < self.min_bytes:
            self._buffer.clear()
            return False
        pcm = bytes(self._buffer)
        self._buffer.clear()
        try:
            audio = sr.AudioData(pcm, self.sample_rate, 2)
            heard = self.recognizer.recognize_google(audio, language="es-ES")
        except Exception:
            return False
        words = _normalize(heard).replace(",", " ").replace(".", " ").split()
        return self.keyword in words


def create_orion_phrase_engine(keyword="orion"):
    return OrionPhraseEngine(keyword=keyword)
