from gever.brain import GeversBrain


def make_brain():
    import threading
    brain = GeversBrain.__new__(GeversBrain)
    brain._messages_lock = threading.Lock()
    brain._lead_tools_lock = threading.Lock()
    return brain


def test_natural_graph_request_is_recognized():
    brain = make_brain()
    assert brain._is_lead_graph_command("pon las gráficas de la búsqueda") is True
    assert brain._is_lead_graph_command("muestra los gráficos de los resultados") is True


def test_unrelated_graph_request_is_not_treated_as_lead_graphs():
    brain = make_brain()
    assert brain._is_lead_graph_command("haz una gráfica del clima") is False


def test_default_language_directive_forces_spanish_over_old_memory():
    brain = make_brain()
    directive = brain._language_directive("ahora dime qué encontraste")
    assert "EXCLUSIVAMENTE EN ESPAÑOL" in directive
    assert "memoria" in directive.lower()


def test_explicit_english_request_allows_english():
    brain = make_brain()
    directive = brain._language_directive("dímelo en inglés")
    assert "INGLÉS" in directive
