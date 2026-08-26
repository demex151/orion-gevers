import os
import tempfile
import threading

import edge_tts
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from starlette.background import BackgroundTask

from gever.brain import GeversBrain
from gever.clap import ClapDetector
from gever.commands import is_close_session_command
from gever.conversation_audio import ConversationAudioState
from gever.listen import GeversListener
from gever.openwakeword_engine import create_openwakeword_engine
from gever.sentinel import SentinelMonitor
from gever.session import SessionController, SessionState
from gever.speech_director import GeversSpeechDirector
from gever.voice import GeversVoice, VOICE, VOICE_RATE, VOICE_PITCH, VOICE_VOLUME
from gever.wakeword import WakeWordDetector


app = FastAPI(title="GEVER Backend", version="2.0.0")

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

brain = GeversBrain()
listener = GeversListener()
voice_cleaner = GeversVoice()
speech_director = GeversSpeechDirector()
conversation_audio = ConversationAudioState()

clap_detector = ClapDetector()
wake_detector = WakeWordDetector(
    engine_factory=create_openwakeword_engine,
    keyword="orion",
)
sentinel = SentinelMonitor(clap_detector, wake_detector)
session_controller = SessionController(sentinel, conversation_audio)

microphone_lock = threading.Lock()


class ChatRequest(BaseModel):
    message: str


class SpeakRequest(BaseModel):
    text: str


class OpenSessionRequest(BaseModel):
    trigger: str = "manual"


@app.on_event("startup")
def startup_audio():
    try:
        session_controller.start()
    except Exception as exc:
        print(f"[SENTINEL] No pudo iniciar: {exc}")


@app.on_event("shutdown")
def shutdown_audio():
    try:
        session_controller.stop()
    except Exception:
        pass


@app.get("/")
def root():
    return {
        "name": "GEVER",
        "status": "online",
        "version": "2.0.0",
        "wake_word": "ORION",
        "activation": ["ORION", "DOUBLE_CLAP"],
    }


@app.get("/api/status")
def status():
    snapshot = session_controller.snapshot()
    return {
        "status": "online",
        "brain": "ready",
        "memory": "connected",
        "microphone": "ready",
        "voice": "ready",
        "wake_word": "ORION",
        "wake_local_available": wake_detector.available,
        "wake_local_error": wake_detector.error,
        "session": snapshot,
        "voice_model": VOICE,
        "voice_rate": VOICE_RATE,
        "voice_pitch": VOICE_PITCH,
    }


@app.get("/api/session/status")
def session_status():
    result = session_controller.snapshot()
    result["wake_local_available"] = wake_detector.available
    result["wake_local_error"] = wake_detector.error
    result["double_clap_available"] = True
    return result


@app.post("/api/session/open")
def session_open(request: OpenSessionRequest):
    if conversation_audio.is_active:
        return {"ok": False, "error": "El micrófono conversacional todavía está ocupado."}
    conversation_audio.reset()
    result = session_controller.open_session(request.trigger)
    return {"ok": True, **result}


@app.post("/api/session/close")
def session_close():
    try:
        result = session_controller.close_session("ui")
        return {"ok": True, **result}
    except Exception as exc:
        return {"ok": False, "error": str(exc), **session_controller.snapshot()}


@app.get("/api/memories")
def memories():
    try:
        return {"ok": True, "memories": brain.memories()}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


@app.post("/api/chat")
def chat(request: ChatRequest):
    message = request.message.strip()
    if not message:
        return {"ok": False, "error": "Mensaje vacío"}
    try:
        answer = brain.think(message)
        return {"ok": True, "answer": answer}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _capture_session_utterance():
    if session_controller.state != SessionState.SESSION:
        return {"ok": False, "inactive": True, "error": "GEVER no está en una sesión activa."}

    if not conversation_audio.begin():
        return {"ok": False, "closed": True, "error": "La sesión está cerrándose."}

    try:
        with microphone_lock:
            text = listener.listen()
    finally:
        conversation_audio.finish()

    if conversation_audio.cancel_requested:
        return {"ok": False, "closed": True, "discarded": True}

    if not text:
        return {"ok": False, "error": "No se detectó ninguna frase."}

    if text.startswith("ERROR_RECONOCIMIENTO:"):
        return {"ok": False, "error": text}

    print(f"[CONVERSACION] Escuchado: {text}")

    if is_close_session_command(text):
        try:
            result = session_controller.close_session("voice")
            return {"ok": True, "closed": True, "text": text, **result}
        except Exception as exc:
            return {"ok": False, "closed": True, "error": str(exc)}

    return {"ok": True, "closed": False, "text": text}


@app.post("/api/session/listen")
def session_listen():
    return _capture_session_utterance()


@app.post("/api/listen")
def listen_legacy():
    return _capture_session_utterance()


@app.post("/api/wake-listen")
def wake_listen_legacy():
    snapshot = session_controller.snapshot()
    return {
        "ok": True,
        "activated": snapshot["state"] == SessionState.SESSION.value,
        "heard": "",
        "command": "",
        "wake_word": "ORION",
        "legacy": True,
        **snapshot,
    }


def remove_temp_file(path):
    try:
        os.remove(path)
    except OSError:
        pass


@app.post("/api/tts")
async def text_to_speech(request: SpeakRequest):
    directed_text = speech_director.direct(request.text)
    text = voice_cleaner.clean_for_speech(directed_text)

    if not text:
        return {"ok": False, "error": "Texto vacío después de limpiar."}

    print(f"[TTS DIRIGIDO]: {text}")

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
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
        return FileResponse(
            path=temp_path,
            media_type="audio/mpeg",
            filename="gever-response.mp3",
            background=BackgroundTask(remove_temp_file, temp_path),
        )
    except Exception:
        remove_temp_file(temp_path)
        raise
