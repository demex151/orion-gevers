class WakeWordDetector:
    """Pluggable ORION detector with explicit degraded mode."""

    def __init__(self, engine_factory=None, keyword="orion"):
        self.keyword = keyword.lower().strip()
        self.engine = None
        self.available = False
        self.error = None

        if engine_factory is None:
            self.error = "No compatible ORION engine configured"
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
            return False

    def flush(self) -> bool:
        if not self.available or not self.engine:
            return False
        flush = getattr(self.engine, "flush", None)
        if not callable(flush):
            return False
        try:
            return bool(flush())
        except Exception as exc:
            self.error = str(exc)
            return False
