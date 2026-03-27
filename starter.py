"""
starter.py — Arranca Sincroniza en MODO DESARROLLO.

Flujo:
  1. Lanza «npm run build -- --watch» para mantener frontend/dist/ actualizado.
  2. Espera a que se genere dist/index.html (primera compilación).
  3. Crea la ventana pywebview apuntando al bundle local (file://).
  4. Vigila cambios en dist/ → recarga automática de la ventana (hot reload).
  5. Vigila cambios en backend/ → avisa por consola (requiere reinicio).

Uso::

    python starter.py

Los selectores de directorio (pywebview.api.despachar) funcionan porque la
ventana es una ventana nativa, no un navegador externo.
"""

from __future__ import annotations

import os
import subprocess
import sys
import threading
import time
from pathlib import Path

# ── Rutas ─────────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent
FRONTEND_DIR = BASE_DIR / "frontend"
DIST_DIR = FRONTEND_DIR / "dist"
FRONTEND_URL = (DIST_DIR / "index.html").as_uri()

# Añadir el backend al path para que los imports de app.* funcionen
sys.path.insert(0, str(BASE_DIR / "backend"))

# ── Hot reload ────────────────────────────────────────────────────────────────

try:
    from watchdog.observers import Observer  # type: ignore[import-untyped]
    from watchdog.events import FileSystemEventHandler  # type: ignore[import-untyped]
    WATCHDOG_DISPONIBLE = True
except ImportError:
    WATCHDOG_DISPONIBLE = False
    print("[WARNING] watchdog no instalado — sin hot reload. "
          "Instala con: pip install watchdog")


class _FrontendHandler(FileSystemEventHandler if WATCHDOG_DISPONIBLE else object):  # type: ignore[misc]
    """Recarga la ventana cuando cambia el bundle de Vite."""

    def __init__(self, ventana, debounce: float = 1.5) -> None:
        self._ventana = ventana
        self._debounce = debounce
        self._timer: threading.Timer | None = None
        self._last: float = 0.0

    def on_modified(self, event) -> None:
        if event.is_directory:
            return
        path = event.src_path if isinstance(event.src_path, str) else event.src_path.decode()
        if "dist" in path and path.endswith((".html", ".js", ".css")):
            self._programar_recarga()

    def _programar_recarga(self) -> None:
        if self._timer:
            self._timer.cancel()
        self._timer = threading.Timer(self._debounce, self._recargar)
        self._timer.start()

    def _recargar(self) -> None:
        if time.time() - self._last < self._debounce:
            return
        self._last = time.time()
        try:
            self._ventana.evaluate_js("location.reload()")
            print("[RELOAD] Cambios detectados en frontend — ventana recargada.")
        except Exception as exc:
            print(f"[WARNING] Error al recargar ventana: {exc}")


class _BackendHandler(FileSystemEventHandler if WATCHDOG_DISPONIBLE else object):  # type: ignore[misc]
    """Notifica cuando cambia un archivo Python del backend."""

    def __init__(self, ventana, cooldown: float = 10.0) -> None:
        self._ventana = ventana
        self._cooldown = cooldown
        self._last: float = 0.0

    def on_modified(self, event) -> None:
        if event.is_directory:
            return
        path = event.src_path if isinstance(event.src_path, str) else event.src_path.decode()
        if path.endswith(".py"):
            now = time.time()
            if now - self._last < self._cooldown:
                return
            self._last = now
            nombre = os.path.basename(path)
            print(f"[BACKEND] Cambio detectado en {nombre} — reinicia la app para aplicarlo.")


def _iniciar_watchers(ventana):
    if not WATCHDOG_DISPONIBLE:
        return None, None

    frontend_observer = Observer()
    frontend_observer.schedule(_FrontendHandler(ventana), str(DIST_DIR), recursive=True)
    frontend_observer.start()
    print("[WATCH] Observando frontend/dist/ …")

    backend_observer = Observer()
    backend_observer.schedule(_BackendHandler(ventana), str(BASE_DIR / "backend"), recursive=True)
    backend_observer.start()
    print("[WATCH] Observando backend/ …")

    return frontend_observer, backend_observer


# ── Frontend build watch ──────────────────────────────────────────────────────

def _lanzar_build_watch() -> subprocess.Popen:
    print("[BUILD] Lanzando npm run build --watch …")
    return subprocess.Popen(
        ["npm", "run", "build", "--", "--watch"],
        cwd=str(FRONTEND_DIR),
        shell=True,
    )


def _esperar_primer_build(timeout: int = 30) -> bool:
    index = DIST_DIR / "index.html"
    print("[BUILD] Esperando primera compilación …")
    for _ in range(timeout * 2):
        if index.exists():
            print("[BUILD] Primera compilación completada.")
            return True
        time.sleep(0.5)
    print("[ERROR] Tiempo de espera agotado — no se encontró dist/index.html")
    return False


# ── pywebview ─────────────────────────────────────────────────────────────────

def _crear_ventana():
    import webview  # type: ignore[import-untyped]
    from main import Api, _construir_servicios, _DATA_DIR  # noqa: PLC0415
    from app.api.dispatcher import Dispatcher  # noqa: PLC0415
    from app.api.eventos import crear_emisor_evento  # noqa: PLC0415
    from app.api.registro import registrar_todos  # noqa: PLC0415

    servicios = _construir_servicios(_DATA_DIR)
    dispatcher = Dispatcher()
    api = Api(dispatcher)

    ventana = webview.create_window(
        title="Sincroniza [DEV]",
        url=FRONTEND_URL,
        js_api=api,
        width=1280,
        height=800,
        min_size=(800, 600),
    )

    def on_loaded() -> None:
        emisor = crear_emisor_evento(ventana)
        servicios.log_servicio.establecer_callback(emisor)
        registrar_todos(dispatcher, servicios, ventana)

    return ventana, on_loaded


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    npm_proc = _lanzar_build_watch()
    frontend_obs = backend_obs = None

    try:
        if not _esperar_primer_build():
            npm_proc.terminate()
            sys.exit(1)

        ventana, on_loaded = _crear_ventana()
        frontend_obs, backend_obs = _iniciar_watchers(ventana)

        import webview  # type: ignore[import-untyped]
        webview.start(on_loaded, debug=True)

    finally:
        print("\n[STOP] Cerrando recursos …")
        if frontend_obs:
            frontend_obs.stop()
            frontend_obs.join()
        if backend_obs:
            backend_obs.stop()
            backend_obs.join()
        npm_proc.terminate()
        print("[STOP] Listo.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
