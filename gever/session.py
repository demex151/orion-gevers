import threading
import time
from enum import Enum


class SessionState(str, Enum):
    SENTINEL = "SENTINEL"
    SESSION = "SESSION"
    STOPPED = "STOPPED"


class SessionController:
    """Own GEVER's audio lifecycle and prevent competing microphone loops."""

    def __init__(self, sentinel, conversation, release_timeout=1.5):
        self.sentinel = sentinel
        self.conversation = conversation
        self.release_timeout = release_timeout
        self.state = SessionState.STOPPED
        self.last_trigger = None
        self.last_close_reason = None
        self._lock = threading.RLock()

    def start(self):
        with self._lock:
            if self.state == SessionState.SENTINEL:
                return self.snapshot()
            self.conversation.cancel()
            self.sentinel.start(self._on_sentinel_activate)
            self.state = SessionState.SENTINEL
            return self.snapshot()

    def _on_sentinel_activate(self, trigger):
        self.open_session(trigger)

    def open_session(self, trigger="manual"):
        with self._lock:
            if self.state == SessionState.SESSION:
                return self.snapshot()
            self.sentinel.stop()
            self.last_trigger = trigger
            self.state = SessionState.SESSION
            return self.snapshot()

    def close_session(self, reason="manual"):
        with self._lock:
            if self.state == SessionState.STOPPED:
                return self.snapshot()
            self.conversation.cancel()
            deadline = time.monotonic() + self.release_timeout
            while self.conversation.is_active and time.monotonic() < deadline:
                time.sleep(0.01)
            if self.conversation.is_active:
                raise TimeoutError("Conversational microphone did not release in time")
            self.last_close_reason = reason
            self.sentinel.start(self._on_sentinel_activate)
            self.state = SessionState.SENTINEL
            return self.snapshot()

    def stop(self):
        with self._lock:
            self.conversation.cancel()
            self.sentinel.stop()
            self.state = SessionState.STOPPED
            return self.snapshot()

    def snapshot(self):
        return {
            "state": self.state.value,
            "last_trigger": self.last_trigger,
            "last_close_reason": self.last_close_reason,
        }
