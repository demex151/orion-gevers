import pytest
from gever.tasks.models import Capability
from gever.tasks.registry import TaskRegistry
from gever.tasks.router import TaskRouter


class FakeCapability(Capability):
    name = "fake"
    signals = ("haz tarea", "ejecuta prueba")
    def execute(self, context): return context
    def verify(self, result): return True


def test_registry_registers_and_resolves_capability():
    registry=TaskRegistry(); capability=FakeCapability(); registry.register(capability)
    assert registry.get("fake") is capability
    assert registry.resolve("ORION, haz tarea ahora") is capability


def test_registry_rejects_duplicate_name():
    registry=TaskRegistry(); registry.register(FakeCapability())
    with pytest.raises(ValueError): registry.register(FakeCapability())


def test_router_returns_none_for_normal_conversation():
    registry=TaskRegistry(); registry.register(FakeCapability()); router=TaskRouter(registry)
    assert router.route("cómo estás hoy") is None


def test_matching_is_accent_and_case_insensitive():
    class AccentCapability(FakeCapability):
        name="accent"; signals=("búsqueda rápida",)
    registry=TaskRegistry(); capability=AccentCapability(); registry.register(capability)
    assert registry.resolve("BUSQUEDA RAPIDA") is capability
