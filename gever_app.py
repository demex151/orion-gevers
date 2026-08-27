"""
GEVER launcher.

Primary desktop entry point. It starts the FastAPI backend and the React/Vite
interface so `python gever_app.py` opens the current GEVER visual experience.
The previous CustomTkinter UI is preserved in `gever_legacy_app.py`.
"""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time
import webbrowser


ROOT = Path(__file__).resolve().parent
FRONTEND = ROOT / "frontend"
BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 8000
FRONTEND_HOST = "127.0.0.1"
FRONTEND_PORT = 5173
FRONTEND_URL = f"http://{FRONTEND_HOST}:{FRONTEND_PORT}"


def _wait_for_port(host: str, port: int, timeout: float = 30.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.25)
    return False


def _npm_executable() -> str:
    candidates = ["npm.cmd", "npm"] if os.name == "nt" else ["npm", "npm.cmd"]
    for candidate in candidates:
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    raise RuntimeError(
        "No encontré npm. Instala Node.js y vuelve a ejecutar: python gever_app.py"
    )


def _ensure_frontend_dependencies(npm: str) -> None:
    if (FRONTEND / "node_modules").exists():
        return
    print("[GEVER] Instalando dependencias del frontend por primera vez...")
    subprocess.run([npm, "install"], cwd=FRONTEND, check=True)


def _start_backend() -> subprocess.Popen:
    print("[GEVER] Iniciando cerebro y API...")
    return subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "backend.server:app",
            "--host",
            BACKEND_HOST,
            "--port",
            str(BACKEND_PORT),
        ],
        cwd=ROOT,
    )


def _start_frontend(npm: str) -> subprocess.Popen:
    print("[GEVER] Iniciando interfaz visual...")
    return subprocess.Popen(
        [
            npm,
            "run",
            "dev",
            "--",
            "--host",
            FRONTEND_HOST,
            "--port",
            str(FRONTEND_PORT),
        ],
        cwd=FRONTEND,
    )


def _stop_process(process: subprocess.Popen | None) -> None:
    if process is None or process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


def main() -> int:
    npm = _npm_executable()
    _ensure_frontend_dependencies(npm)

    backend = None
    frontend = None

    try:
        backend = _start_backend()
        if not _wait_for_port(BACKEND_HOST, BACKEND_PORT):
            raise RuntimeError(
                "El backend de GEVER no abrió el puerto 8000. "
                "Revisa los errores mostrados arriba."
            )

        frontend = _start_frontend(npm)
        if not _wait_for_port(FRONTEND_HOST, FRONTEND_PORT):
            raise RuntimeError(
                "La interfaz de GEVER no abrió el puerto 5173. "
                "Revisa los errores mostrados arriba."
            )

        print(f"[GEVER] Sistema listo: {FRONTEND_URL}")
        webbrowser.open(FRONTEND_URL)

        while True:
            if backend.poll() is not None:
                raise RuntimeError("El backend de GEVER se cerró inesperadamente.")
            if frontend.poll() is not None:
                raise RuntimeError("La interfaz de GEVER se cerró inesperadamente.")
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n[GEVER] Cerrando sistema...")
        return 0
    except Exception as exc:
        print(f"\n[GEVER] ERROR: {exc}")
        return 1
    finally:
        _stop_process(frontend)
        _stop_process(backend)


if __name__ == "__main__":
    raise SystemExit(main())
