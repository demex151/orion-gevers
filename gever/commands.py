import re
import unicodedata


def _normalize(text: str) -> str:
    value = unicodedata.normalize("NFD", str(text or "").lower())
    value = "".join(ch for ch in value if unicodedata.category(ch) != "Mn")
    value = re.sub(r"[^a-z0-9\s]", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def is_close_session_command(text: str) -> bool:
    """Return True only for explicit commands to end GEVER's current session."""
    value = _normalize(text)
    if not value:
        return False

    exact = {
        "cierra la sesion",
        "cerrar la sesion",
        "cerremos la sesion",
        "cierra el chat",
        "cerrar el chat",
        "cerremos el chat",
        "finaliza la conversacion",
        "finalizar la conversacion",
        "termina la conversacion",
        "terminemos la conversacion",
        "deja de escuchar",
        "para de escuchar",
        "terminemos",
        "terminemos por ahora",
        "hasta aqui",
    }
    if value in exact:
        return True

    # Permit a direct address to GEVER/ORION without making substring matching broad.
    for prefix in ("orion ", "gever "):
        if value.startswith(prefix):
            return value[len(prefix):] in exact

    return False
