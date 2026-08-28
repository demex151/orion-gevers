"""Contracts shared by registered capabilities and the task runtime."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any
import unicodedata


def normalize_command(text):
    text = unicodedata.normalize("NFKD", str(text or ""))
    return " ".join("".join(c for c in text if not unicodedata.combining(c)).casefold().split())


class TaskStatus(str, Enum):
    STARTED = "started"
    RUNNING = "running"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class TaskOutcome:
    task_id: str
    capability: str
    status: TaskStatus
    started_at: datetime
    finished_at: datetime
    result: Any = None
    error: str | None = None
    verified: bool = False


class Capability(ABC):
    name = ""
    signals = ()

    def matches(self, text):
        normalized = normalize_command(text)
        return any(normalize_command(s) and normalize_command(s) in normalized for s in self.signals)

    @abstractmethod
    def execute(self, context):
        """Execute this capability and return its result."""

    @abstractmethod
    def verify(self, result):
        """Return True only when the result satisfies this capability's contract."""

    def format_response(self, result):
        return str(result)
