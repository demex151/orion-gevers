"""Synchronous worker lifecycle. Observers cannot change execution results."""

from datetime import datetime, timezone
from collections import deque
from threading import Lock
from uuid import uuid4

from .models import TaskOutcome, TaskStatus


class TaskRuntime:
    def __init__(self, progress_callback=None):
        self.progress_callback = progress_callback
        self.last_outcome = None
        self._events = deque(maxlen=100)
        self._events_lock = Lock()

    def progress_snapshot(self):
        with self._events_lock:
            return [dict(event) for event in self._events]

    def run_steps(self, capabilities, context):
        """Run explicitly supplied steps, forwarding only verified results.

        This is sequential orchestration, not an autonomous planner or sandbox.
        Each worker receives the original input and the previous worker's result.
        """
        outcomes = []
        previous = None
        for capability in capabilities:
            outcome = self.run(capability, {"input": context, "previous_result": previous})
            outcomes.append(outcome)
            if not outcome.verified:
                break
            previous = outcome.result
        return outcomes

    def _emit(self, task_id, capability, status):
        event = {"task_id": task_id, "capability": capability.name, "status": status.value,
                 "timestamp": datetime.now(timezone.utc).isoformat()}
        with self._events_lock:
            self._events.append(event)
        if self.progress_callback is not None:
            try:
                self.progress_callback(dict(event))
            except Exception:
                pass  # Progress is observational; a disconnected UI cannot fail a task.

    def run(self, capability, context):
        task_id = str(uuid4())
        started_at = datetime.now(timezone.utc)
        result, error, verified = None, None, False
        self._emit(task_id, capability, TaskStatus.STARTED)
        try:
            self._emit(task_id, capability, TaskStatus.RUNNING)
            result = capability.execute(context)
            self._emit(task_id, capability, TaskStatus.VERIFYING)
            verified = capability.verify(result) is True
            if not verified:
                error = "El resultado no superó la verificación."
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
        status = TaskStatus.COMPLETED if verified else TaskStatus.FAILED
        outcome = TaskOutcome(task_id, capability.name, status, started_at,
                              datetime.now(timezone.utc), result, error, verified)
        self.last_outcome = outcome
        self._emit(task_id, capability, status)
        return outcome
