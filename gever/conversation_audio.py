import threading


class ConversationAudioState:
    """Tracks conversational microphone ownership for SessionController.

    The current speech-recognition call itself is blocking, so cancellation is
    cooperative: closing a session prevents another listen from starting and
    marks the active request for discard when it returns. Sentinel restart is
    allowed only after active ownership has cleared.
    """

    def __init__(self):
        self._active = False
        self._cancel_requested = False
        self._lock = threading.RLock()

    @property
    def is_active(self):
        with self._lock:
            return self._active

    @property
    def cancel_requested(self):
        with self._lock:
            return self._cancel_requested

    def begin(self):
        with self._lock:
            if self._cancel_requested:
                return False
            self._active = True
            return True

    def finish(self):
        with self._lock:
            self._active = False

    def cancel(self):
        with self._lock:
            self._cancel_requested = True

    def reset(self):
        with self._lock:
            if self._active:
                raise RuntimeError("Cannot reset conversation audio while active")
            self._cancel_requested = False
