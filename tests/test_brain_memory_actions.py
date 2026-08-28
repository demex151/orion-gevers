from gever.brain import GeversBrain
from test_memory import make_memory


def make_brain_with_real_memory(tmp_path):
    """A GeversBrain wired to a real, isolated GeversMemory instance so we
    exercise the actual remember/update_by_id/forget_by_id contract instead
    of a mock that could hide a wrong method name."""
    brain = GeversBrain.__new__(GeversBrain)
    brain.memory = make_memory(tmp_path)
    return brain


def test_create_action_actually_persists_a_memory(tmp_path):
    brain = make_brain_with_real_memory(tmp_path)

    brain._apply_memory_action({
        "action": "CREATE",
        "content": "Le gusta trabajar temprano",
        "category": "preference",
    })

    stored = brain.memory.get_all()
    assert len(stored) == 1
    assert stored[0]["content"] == "Le gusta trabajar temprano"


def test_update_action_actually_changes_stored_content(tmp_path):
    brain = make_brain_with_real_memory(tmp_path)
    brain.memory.remember("Contenido original", category="fact")
    memory_id = brain.memory.get_all()[0]["id"]

    brain._apply_memory_action({
        "action": "UPDATE",
        "id": memory_id,
        "content": "Contenido corregido",
    })

    assert brain.memory.get_all()[0]["content"] == "Contenido corregido"


def test_delete_action_actually_removes_the_memory(tmp_path):
    brain = make_brain_with_real_memory(tmp_path)
    brain.memory.remember("Para borrar", category="fact")
    memory_id = brain.memory.get_all()[0]["id"]

    brain._apply_memory_action({"action": "DELETE", "id": memory_id})

    assert brain.memory.get_all() == []


def test_none_action_does_nothing_and_does_not_raise(tmp_path):
    brain = make_brain_with_real_memory(tmp_path)

    brain._apply_memory_action({"action": "NONE"})

    assert brain.memory.get_all() == []


def test_malformed_action_is_swallowed_without_raising(tmp_path):
    brain = make_brain_with_real_memory(tmp_path)

    # Missing "content" for CREATE must not raise out of think()'s call site.
    brain._apply_memory_action({"action": "CREATE"})

    assert brain.memory.get_all() == []
