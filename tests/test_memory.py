from gever.memory import GeversMemory


def make_memory(tmp_path):
    """Build a GeversMemory instance isolated to tmp_path, bypassing the
    hardcoded data/memory.json path used by the real constructor."""
    memory = GeversMemory.__new__(GeversMemory)
    memory.project_root = tmp_path
    memory.data_dir = tmp_path / "data"
    memory.data_dir.mkdir(exist_ok=True)
    memory.memory_file = memory.data_dir / "memory.json"
    memory.memories = memory._load()
    memory._ensure_ids()
    return memory


def test_remember_persists_across_instances_and_rejects_duplicates(tmp_path):
    memory = make_memory(tmp_path)

    assert memory.remember("Le gusta el color azul", category="preference") is True
    assert memory.remember("Le gusta el color azul", category="preference") is False
    assert len(memory.get_all()) == 1

    reloaded = make_memory(tmp_path)
    assert len(reloaded.get_all()) == 1
    assert reloaded.get_all()[0]["content"] == "Le gusta el color azul"


def test_update_by_id_changes_content_and_category(tmp_path):
    memory = make_memory(tmp_path)
    memory.remember("Prefiere hablar en espanol", category="preference")
    memory_id = memory.get_all()[0]["id"]

    assert memory.update_by_id(memory_id, "Prefiere hablar en ingles", category="preference") is True
    assert memory.get_all()[0]["content"] == "Prefiere hablar en ingles"
    assert memory.update_by_id("no-existe", "x") is False


def test_forget_by_id_removes_only_that_memory(tmp_path):
    memory = make_memory(tmp_path)
    memory.remember("Recuerdo uno")
    memory.remember("Recuerdo dos")
    first_id = memory.get_all()[0]["id"]

    assert memory.forget_by_id(first_id) is True
    remaining = memory.get_all()
    assert len(remaining) == 1
    assert remaining[0]["content"] == "Recuerdo dos"
    assert memory.forget_by_id(first_id) is False


def test_memory_has_no_add_update_delete_methods(tmp_path):
    """Regression guard: GeversBrain must call remember/update_by_id/forget_by_id,
    never add/update/delete, which GeversMemory has never implemented."""
    memory = make_memory(tmp_path)
    assert not hasattr(memory, "add")
    assert not hasattr(memory, "update")
    assert not hasattr(memory, "delete")
