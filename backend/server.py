import os
import re
import tempfile
import threading
import unicodedata

import edge_tts

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from starlette.background import BackgroundTask

from gever.brain import GeversBrain
from gever.listen import GeversListener
from gever.voice import (
    GeversVoice,
    VOICE,
    VOICE_RATE,
    VOICE_PITCH,
    VOICE_VOLUME,
)


# =========================================================
# CONFIGURACIÓN
# =========================================================

WAKE_WORD = "orion"


app = FastAPI(
    title="GEVER Backend",
    version="1.9.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# SISTEMAS
# =========================================================

brain = GeversBrain()
listener = GeversListener()
voice_cleaner = GeversVoice()


# =========================================================
# CONTROL DEL MICRÓFONO + DIAGNÓSTICO TTS
# =========================================================

microphone_lock = threading.Lock()
tts_counter_lock = threading.Lock()
tts_request_counter = 0


def next_tts_request_id():
    global tts_request_counter
    with tts_counter_lock:
        tts_request_counter += 1
        return tts_request_counter


# =========================================================
# MODELOS
# =========================================================

class ChatRequest(BaseModel):
    message: str


class SpeakRequest(BaseModel):
    text: str


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():
    return {
        "name": "GEVER",
        "status": "online",
        "version": "1.9.0",
        "wake_word": "ORION",
    }


# =========================================================
# STATUS
# =========================================================

@app.get("/api/status")
def status():
    return {
        "status": "online",
        "brain": "ready",
        "memory": "connected",
        "microphone": "ready",
        "voice": "ready",
        "wake_word": "ORION",
        "voice_model": VOICE,
        "voice_rate": VOICE_RATE,
        "voice_pitch": VOICE_PITCH,
    }


# =========================================================
# MEMORIA
# =========================================================

@app.get("/api/memories")
def memories():
    try:
        return {
            "ok": True,
            "memories": brain.memories(),
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
        }


# =========================================================
# CHAT
# =========================================================

@app.post("/api/chat")
def chat(request: ChatRequest):
    message = request.message.strip()

    if not message:
        return {
            "ok": False,
            "error": "Mensaje vacío",
        }

    try:
        answer = brain.think(message)
        return {
            "ok": True,
            "answer": answer,
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
        }


# =========================================================
# QUITAR ACENTOS
# =========================================================

def remove_accents(text):
    normalized = unicodedata.normalize("NFD", str(text))
    return "".join(
        char
        for char in normalized
        if unicodedata.category(char) != "Mn"
    )


# =========================================================
# NORMALIZAR TEXTO WAKE
# =========================================================

def normalize_wake_text(text):
    if not text:
        return ""

    normalized = remove_accents(str(text).lower())
    normalized = (
        normalized
        .replace("¿", "")
        .replace("?", "")
        .replace("¡", "")
        .replace("!", "")
        .replace(",", " ")
        .replace(".", " ")
        .replace(":", " ")
        .replace(";", " ")
    )
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


# =========================================================
# DETECTAR ORION
# =========================================================

def detect_wake_word(text):
    normalized = normalize_wake_text(text)
    print(f"[WAKE NORMALIZADO]: {normalized}")

    if not normalized:
        return False, ""

    words = normalized.split()

    if WAKE_WORD not in words:
        return False, ""

    position = words.index(WAKE_WORD)
    command = " ".join(words[position + 1:]).strip()
    return True, command


# =========================================================
# ESCUCHA NORMAL
# =========================================================

@app.post("/api/listen")
def listen():
    try:
        with microphone_lock:
            text = listener.listen(
                timeout=None,
                phrase_time_limit=None
            )

        if not text:
            return {
                "ok": False,
                "error": "No se detectó ninguna frase.",
            }

        if text.startswith("ERROR_RECONOCIMIENTO:"):
            return {
                "ok": False,
                "error": text,
            }

        print(f"[CONVERSACION] Escuchado: {text}")
        return {
            "ok": True,
            "text": text,
        }

    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
        }


# =========================================================
# ESCUCHA DE ORION
# =========================================================

@app.post("/api/wake-listen")
def wake_listen():
    try:
        with microphone_lock:
            text = listener.listen_wake()

        if not text:
            return {
                "ok": True,
                "activated": False,
                "heard": "",
                "command": "",
                "wake_word": "ORION",
            }

        if text.startswith("ERROR_RECONOCIMIENTO:"):
            return {
                "ok": False,
                "activated": False,
                "heard": text,
                "command": "",
                "wake_word": "ORION",
                "error": text,
            }

        activated, command = detect_wake_word(text)
        print(f"[WAKE] Escuchado: {text}")

        if activated:
            print("[WAKE] ORION DETECTADO")
            print("[WAKE] GEVER ACTIVADO")
            if command:
                print(f"[WAKE] Instrucción: {command}")

        return {
            "ok": True,
            "activated": activated,
            "heard": text,
            "command": command,
            "wake_word": "ORION",
        }

    except Exception as e:
        return {
            "ok": False,
            "activated": False,
            "heard": "",
            "command": "",
            "wake_word": "ORION",
            "error": str(e),
        }


# =========================================================
# ARCHIVOS TEMPORALES
# =========================================================

def remove_temp_file(path):
    try:
        os.remove(path)
    except OSError:
        pass


# =========================================================
# TEXT TO SPEECH
# =========================================================

@app.post("/api/tts")
async def text_to_speech(request: SpeakRequest):
    request_id = next_tts_request_id()

    text = voice_cleaner.clean_for_speech(request.text)

    print(
        f"[TTS REQUEST #{request_id}] "
        f"chars={len(text)} text={text[:120]!r}"
    )

    if not text:
        print(f"[TTS REQUEST #{request_id}] RECHAZADO: texto vacío")
        return {
            "ok": False,
            "error": "Texto vacío después de limpiar.",
        }

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp3"
    )
    temp_path = temp_file.name
    temp_file.close()

    try:
        communicator = edge_tts.Communicate(
            text=text,
            voice=VOICE,
            rate=VOICE_RATE,
            pitch=VOICE_PITCH,
            volume=VOICE_VOLUME,
        )

        await communicator.save(temp_path)
        print(f"[TTS REQUEST #{request_id}] AUDIO GENERADO")

        return FileResponse(
            path=temp_path,
            media_type="audio/mpeg",
            filename="gever-response.mp3",
            background=BackgroundTask(
                remove_temp_file,
                temp_path
            ),
        )

    except Exception as error:
        print(
            f"[TTS REQUEST #{request_id}] ERROR: "
            f"{type(error).__name__}: {error}"
        )
        remove_temp_file(temp_path)
        raise
