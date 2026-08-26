import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import asyncio
import re
import tempfile
import unicodedata

import edge_tts
import pygame


# =========================================================
# CONFIGURACIÓN DE VOZ
# =========================================================

VOICE = "es-US-AlonsoNeural"

VOICE_RATE = "+18%"

VOICE_PITCH = "-1Hz"

VOICE_VOLUME = "+0%"


class GeversVoice:

    def __init__(self):

        pygame.mixer.init()


    # =====================================================
    # LIMPIAR TEXTO PARA VOZ
    # =====================================================

    def clean_for_speech(
        self,
        text
    ):

        if not text:
            return ""

        cleaned = str(text)


        # =================================================
        # LINKS MARKDOWN
        # =================================================

        cleaned = re.sub(
            r"\[([^\]]+)\]\([^)]+\)",
            r"\1",
            cleaned
        )


        # =================================================
        # CÓDIGO / MARKDOWN
        # =================================================

        cleaned = cleaned.replace(
            "```",
            " "
        )

        cleaned = cleaned.replace(
            "`",
            " "
        )

        cleaned = cleaned.replace(
            "**",
            ""
        )

        cleaned = cleaned.replace(
            "__",
            ""
        )

        cleaned = cleaned.replace(
            "*",
            ""
        )


        # =================================================
        # BARRAS Y CARACTERES QUE NO DEBE PRONUNCIAR
        # =================================================

        unwanted_symbols = [
            "/",
            "\\",
            "|",
            "_",
            "~",
            "^",
            "<",
            ">",
            "{",
            "}",
            "[",
            "]",
        ]

        for symbol in unwanted_symbols:

            cleaned = cleaned.replace(
                symbol,
                " "
            )


        # =================================================
        # ENCABEZADOS
        # =================================================

        cleaned = re.sub(
            r"^\s*#+\s*",
            "",
            cleaned,
            flags=re.MULTILINE
        )


        # =================================================
        # VIÑETAS
        # =================================================

        cleaned = re.sub(
            r"^\s*[-•▪◦]+\s*",
            "",
            cleaned,
            flags=re.MULTILINE
        )


        # =================================================
        # EMOJIS
        # =================================================

        result = []

        for char in cleaned:

            code = ord(char)

            category = (
                unicodedata.category(
                    char
                )
            )


            if code in {
                0xFE0E,
                0xFE0F,
                0x200D,
            }:
                continue


            if (
                0x1F000
                <= code
                <= 0x1FAFF
            ):
                continue


            if (
                0x2600
                <= code
                <= 0x27BF
            ):
                continue


            if (
                0x1F1E6
                <= code
                <= 0x1F1FF
            ):
                continue


            if category == "So":
                continue


            # Letras
            if category.startswith("L"):

                result.append(char)

                continue


            # Números
            if category.startswith("N"):

                result.append(char)

                continue


            # Acentos
            if category.startswith("M"):

                result.append(char)

                continue


            # Espacios
            if category.startswith("Z"):

                result.append(char)

                continue


            # Saltos
            if char in "\n\t":

                result.append(" ")

                continue


            # SOLO puntuación útil para hablar.
            if char in {
                ".",
                ",",
                "?",
                "¿",
                "!",
                "¡",
                ":",
                ";",
                "-",
            }:

                result.append(char)


        cleaned = "".join(
            result
        )


        # =================================================
        # HACER EL TEXTO CONVERSACIONAL
        # =================================================

        cleaned = cleaned.replace(
            ";",
            ","
        )

        cleaned = cleaned.replace(
            ":",
            ","
        )


        cleaned = re.sub(
            r"\.{2,}",
            ".",
            cleaned
        )


        cleaned = re.sub(
            r"!{2,}",
            "!",
            cleaned
        )


        cleaned = re.sub(
            r"\?{2,}",
            "?",
            cleaned
        )


        cleaned = re.sub(
            r"\s+([,.!?])",
            r"\1",
            cleaned
        )


        cleaned = re.sub(
            r"([,.!?])([^\s])",
            r"\1 \2",
            cleaned
        )


        cleaned = re.sub(
            r"\s+",
            " ",
            cleaned
        )


        return cleaned.strip()


    # =====================================================
    # GENERAR AUDIO
    # =====================================================

    async def _generate_audio(
        self,
        text,
        output_file
    ):

        communicator = (
            edge_tts.Communicate(
                text=text,
                voice=VOICE,
                rate=VOICE_RATE,
                pitch=VOICE_PITCH,
                volume=VOICE_VOLUME
            )
        )


        await communicator.save(
            output_file
        )


    # =====================================================
    # SPEAK LOCAL
    # =====================================================

    def speak(
        self,
        text
    ):

        if not text:
            return


        speech_text = (
            self.clean_for_speech(
                text
            )
        )


        if not speech_text:
            return


        print(
            f"[VOZ]: {speech_text}"
        )


        temp_file = (
            tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".mp3"
            )
        )


        temp_path = (
            temp_file.name
        )


        temp_file.close()


        try:

            asyncio.run(
                self._generate_audio(
                    speech_text,
                    temp_path
                )
            )


            pygame.mixer.music.load(
                temp_path
            )


            pygame.mixer.music.play()


            while (
                pygame.mixer.music.get_busy()
            ):

                pygame.time.Clock().tick(
                    20
                )


            pygame.mixer.music.unload()


        finally:

            try:

                os.remove(
                    temp_path
                )

            except OSError:

                pass