import os

import numpy as np


class OpenWakeWordEngine:
    """Optional openWakeWord adapter for GEVER's local sentinel.

    A custom ORION .onnx model can be supplied through GEVER_ORION_MODEL.
    If no model is configured, construction fails cleanly and the sentinel
    remains operational through double-clap activation.
    """

    def __init__(self, keyword="orion", model_path=None, threshold=0.55):
        self.keyword = str(keyword or "orion").lower().strip()
        self.model_path = model_path or os.getenv("GEVER_ORION_MODEL", "").strip()
        self.threshold = float(os.getenv("GEVER_ORION_THRESHOLD", threshold))

        if not self.model_path:
            raise RuntimeError("GEVER_ORION_MODEL is not configured")
        if not os.path.isfile(self.model_path):
            raise RuntimeError(f"ORION wake model not found: {self.model_path}")

        from openwakeword.model import Model

        self.model = Model(
            wakeword_models=[self.model_path],
            inference_framework="onnx",
        )

    def feed_pcm16(self, pcm: bytes):
        if not pcm:
            return False
        samples = np.frombuffer(pcm, dtype=np.int16)
        if samples.size == 0:
            return False
        predictions = self.model.predict(samples)
        if not isinstance(predictions, dict) or not predictions:
            return False
        score = max(float(value) for value in predictions.values())
        return score >= self.threshold


def create_openwakeword_engine(keyword="orion"):
    return OpenWakeWordEngine(keyword=keyword)
