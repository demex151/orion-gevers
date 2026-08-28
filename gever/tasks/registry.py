"""Explicit registration; resolving commands never executes a capability."""

from .models import Capability


class TaskRegistry:
    def __init__(self):
        self._capabilities = {}

    def register(self, capability):
        if not isinstance(capability, Capability):
            raise TypeError("Expected a Capability")
        if not isinstance(capability.name, str) or not capability.name.strip():
            raise ValueError("Capability name must not be empty")
        if capability.name in self._capabilities:
            raise ValueError(f"Duplicate capability: {capability.name}")
        self._capabilities[capability.name] = capability

    def get(self, name):
        return self._capabilities.get(name)

    def resolve(self, text):
        # Registration order is the explicit priority when signals overlap.
        return next((c for c in self._capabilities.values() if c.matches(text)), None)
