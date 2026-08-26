class WakeWordDetector:
    """Pluggable local ORION detector with explicit degraded mode.

    The core intentionally has no dependency on PocketSphinx or any other
    native wake-word package. An engine can be injected independently, while
    double-clap activation remains available if voice wake is unavailable.
    Idle audio handled here is never sent to GEVER's brain/chat pipeline.
    """

    def __init__(self, engine_factory=None, keyword="orion"):
        self.keyword = keyword.lower().strip()
        self.engine = None
        self.available = False
        self.error = None

        if engine_factory is None:
            self.error = "No compatible local ORION engine configured"
            return

        try:
            self.engine = engine_factory(self.keyword)
            self.available = self.engine is not None
        except TypeError:
            try:
                self.engine = engine_factory()
                self.available = self.engine is not None
            except Exception as exc:
                self.error = str(exc)
        except Exception as exc:
            self.error = str(exc)

    def feed_pcm16(self, pcm: bytes) -> bool:
        if not self.available or not self.engine or not pcm:
            return False

        try:
            result = self.engine.feed_pcm16(pcm)
            if isinstance(result, bool):
                return result
            heard = str(result or "").lower().strip()
            return self.keyword in heard.split()
        except Exception as exc:
            self.error = str(exc)
            self.available = False
            return False
