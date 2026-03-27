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

    # Incluimos:
    #   frontend/dist  → la app web compilada
    #   data           → directorio de datos (perfiles, historial…)
    #   backend/app    → código del backend (pyinstaller no lo resuelve solo
    #                    porque los imports son dinámicos)
    cmd = (
        f'"{VENV_PYTHON}" -m PyInstaller '
        "--name Sincroniza "
        "--onefile "
        "--windowed "
        f'--add-data "frontend/dist{sep}frontend/dist" '
        f'--add-data "data{sep}data" '
        f'--add-data "backend/app{sep}app" '
        "--hidden-import webview "
        "--hidden-import clr "         # pythonnet / .NET interop
        "--exclude-module PyQt5 "
        "--exclude-module PyQt6 "
        "--exclude-module tkinter "
        f"{icon_opt}"
        "starter_prod.py"
    )
    run(cmd, cwd=BASE_DIR)

    print("\n[OK] Ejecutable generado en la carpeta 'dist/'.")


if __name__ == "__main__":
    main()
