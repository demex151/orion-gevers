import io

import run_lead_hunter


def test_console_text_replaces_unencodable_characters_for_cp1252():
    text = "North Myrtle Beach ▻ Looking for painter"
    rendered = run_lead_hunter.console_text(text, encoding="cp1252")
    rendered.encode("cp1252")
    assert "Looking for painter" in rendered
