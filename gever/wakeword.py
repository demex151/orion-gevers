class WakeWordDetector:
    """Local ORION keyword adapter with explicit degraded mode.

    Idle audio handled here is never sent to GEVER's brain/chat pipeline.
    PocketSphinx is loaded lazily so double-clap activation can remain
    available when the keyword engine is not installed or cannot initialize.
    """

    def __init__(self, decoder_factory=None, keyword="orion"):
        self.keyword = keyword.lower().strip()
        self.decoder = None
        self.available = False
        self.error = None

        try:
            factory = decoder_factory or self._default_decoder_factory
            self.decoder = factory()
            self.available = self.decoder is not None
        except Exception as exc:
            self.error = str(exc)
            self.decoder = None
            self.available = False

    def _default_decoder_factory(self):
        from pocketsphinx import Decoder

        config = Decoder.default_config()
        config.set_string("-keyphrase", self.keyword)
        config.set_float("-kws_threshold", 1e-20)
        decoder = Decoder(config)
        decoder.start_utt()
        return decoder

    def feed_pcm16(self, pcm: bytes) -> bool:
        if not self.available or not self.decoder or not pcm:
            return False

        try:
            self.decoder.process_raw(pcm, False, False)
            hypothesis = self.decoder.hyp()
            if not hypothesis:
                return False
            heard = str(getattr(hypothesis, "hypstr", "")).lower().strip()
            return self.keyword in heard.split()
        except Exception as exc:
            self.error = str(exc)
            self.available = False
            return False
