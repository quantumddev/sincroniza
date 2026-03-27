"""
generar_ejecutable.py — Empaqueta Sincroniza como binario nativo con PyInstaller.

Uso::

    python generar_ejecutable.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).parent
VENV_PYTHON = BASE_DIR / "backend" / "venv" / "Scripts" / "python.exe"
ICON_PATH = BASE_DIR / "icono.ico"


def run(command: str, cwd: Path | None = None) -> None:
    print(f"\n⚡ {command}  (en {cwd or Path.cwd()})")
    try:
        subprocess.run(command, shell=True, check=True, cwd=cwd)
    except subprocess.CalledProcessError as exc:
        print(f"[ERROR] Falló: {command}\n{exc}")
        sys.exit(1)


def main() -> None:
    # ── Validaciones ──────────────────────────────────────────────────────────
    if not VENV_PYTHON.exists():
        print(f"[ERROR] No se encontró el entorno virtual en: {VENV_PYTHON}")
        sys.exit(1)

    # ── 1. Build del frontend ─────────────────────────────────────────────────
    run("npm run build", cwd=BASE_DIR / "frontend")

    # ── 2. PyInstaller ────────────────────────────────────────────────────────
    sep = ";"  # separador de rutas en Windows (en macOS/Linux sería ":")
    icon_opt = f'--icon "{ICON_PATH}" ' if ICON_PATH.exists() else ""

    # Subpaquetes de app/ — PyInstaller no los detecta automáticamente porque
    # muchos imports son dinámicos o están en __init__.py vacíos.
    hidden = " ".join([
        "--hidden-import app",
        # api
        "--hidden-import app.api",
        "--hidden-import app.api.dispatcher",
        "--hidden-import app.api.eventos",
        "--hidden-import app.api.registro",
        # core
        "--hidden-import app.core",
        "--hidden-import app.core.fechas",
        "--hidden-import app.core.fingerprint",
        "--hidden-import app.core.glob_matcher",
        "--hidden-import app.core.hashing",
        "--hidden-import app.core.normalizacion",
        "--hidden-import app.core.validaciones",
        # models
        "--hidden-import app.models",
        "--hidden-import app.models.configuracion",
        "--hidden-import app.models.enums",
        "--hidden-import app.models.error",
        "--hidden-import app.models.evento_log",
        "--hidden-import app.models.nodo_arbol",
        "--hidden-import app.models.perfil",
        "--hidden-import app.models.plan",
        "--hidden-import app.models.regla",
        "--hidden-import app.models.resultado",
        # services
        "--hidden-import app.services",
        "--hidden-import app.services.comparador",
        "--hidden-import app.services.explorador",
        "--hidden-import app.services.historial",
        "--hidden-import app.services.log",
        "--hidden-import app.services.perfiles",
        "--hidden-import app.services.reglas",
        "--hidden-import app.services.sincronizador",
        "--hidden-import app.services.validador",
        # storage
        "--hidden-import app.storage",
        "--hidden-import app.storage.config_storage",
        "--hidden-import app.storage.historial_storage",
        "--hidden-import app.storage.pending_storage",
        # dependencias nativas
        "--hidden-import webview",
        "--hidden-import clr",  # pythonnet / .NET interop
    ])

    # --paths backend  → añade backend/ al sys.path durante el análisis
    # --add-data       → copia archivos no-Python al bundle
    # NOTA: data/ NO se incluye en el bundle; se crea automáticamente junto al
    #       .exe (Path(sys.executable).parent / "data") en el primer arranque.
    cmd = (
        f'"{VENV_PYTHON}" -m PyInstaller '
        "--name Sincroniza "
        "--onefile "
        "--windowed "
        f'--paths "backend" '
        f'--add-data "frontend/dist{sep}frontend/dist" '
        f'--add-data "backend/app{sep}app" '
        "--exclude-module PyQt5 "
        "--exclude-module PyQt6 "
        "--exclude-module tkinter "
        f"{hidden} "
        f"{icon_opt}"
        "starter_prod.py"
    )
    run(cmd, cwd=BASE_DIR)

    print("\n[OK] Ejecutable generado en la carpeta 'dist/'.")


if __name__ == "__main__":
    main()
