import re
import speech_recognition as sr


class GeversListener:

    def __init__(self):

        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # =================================================
        # SENSIBILIDAD
        # =================================================

        self.recognizer.dynamic_energy_threshold = True

        # Permite pausas naturales sin cortar demasiado rápido.
        self.recognizer.pause_threshold = 1.15

        self.recognizer.non_speaking_duration = 0.45

        self.recognizer.phrase_threshold = 0.18


        # =================================================
        # CALIBRACIÓN ÚNICA
        # =================================================

        print("Calibrando micrófono...")

        with self.microphone as source:

            self.recognizer.adjust_for_ambient_noise(
                source,
                duration=0.8
            )

        print("Reconocimiento de voz listo.")

        print(
            f"Umbral de energía: "
            f"{self.recognizer.energy_threshold}"
        )


    # =====================================================
    # NORMALIZAR TEXTO
    # =====================================================

    def normalize_text(self, text):

        if not text:
            return ""

        corrected = str(text).strip()

        variants = [
            r"\bgever\b",
            r"\bhever\b",
            r"\bheber\b",
            r"\bhebert\b",
            r"\bherbert\b",
            r"\bgeber\b",
            r"\bjever\b",
            r"\bever\b",
            r"\beber\b",
            r"\bheffer\b",
        ]

        for pattern in variants:

            corrected = re.sub(
                pattern,
                "GEVER",
                corrected,
                flags=re.IGNORECASE
            )

        return corrected.strip()


    # =====================================================
    # RECONOCER AUDIO
    # =====================================================

    def recognize_audio(self, audio):

        try:

            text = self.recognizer.recognize_google(
                audio,
                language="es-US"
            )

            text = self.normalize_text(
                text
            )

            if text:

                print(
                    f"Escuchado: {text}"
                )

            return text


        except sr.UnknownValueError:

            return ""


        except sr.RequestError as e:

            return (
                "ERROR_RECONOCIMIENTO: "
                f"{e}"
            )


        except Exception as e:

            return (
                "ERROR_RECONOCIMIENTO: "
                f"{e}"
            )


    # =====================================================
    # CONVERSACIÓN NORMAL
    # =====================================================

    def listen(
        self,
        timeout=8,
        phrase_time_limit=15
    ):

        try:

            with self.microphone as source:

                print(
                    "\nHabla ahora..."
                )

                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )

            return self.recognize_audio(
                audio
            )


        except sr.WaitTimeoutError:

            return ""


        except Exception as e:

            return (
                "ERROR_RECONOCIMIENTO: "
                f"{e}"
            )


    # =====================================================
    # ORION
    # =====================================================

    def listen_wake(self):

        try:

            with self.microphone as source:

                print(
                    "\n[WAKE] Esperando ORION..."
                )

                audio = self.recognizer.listen(
                    source,
                    timeout=8,
                    phrase_time_limit=8
                )

            return self.recognize_audio(
                audio
            )


        except sr.WaitTimeoutError:

            return ""


        except Exception as e:

            return (
                "ERROR_RECONOCIMIENTO: "
                f"{e}"
            )