"""
Entrypoint de la aplicación Sincroniza.

Inicializa todos los servicios, construye el Dispatcher JSON-RPC 2.0,
inyecta la API en la ventana pywebview y carga el frontend.

La ventana expone un único método JavaScript ``despachar(json)`` que
recibe y devuelve cadenas JSON conformes a JSON-RPC 2.0.

Uso::

    python main.py            # producción (carga frontend/dist/index.html)
    python main.py --dev      # desarrollo (conecta a http://localhost:5173)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# ── Rutas del proyecto ────────────────────────────────────────────────────────
_BACKEND_DIR = Path(__file__).parent
_DATA_DIR = _BACKEND_DIR.parent / "data"
_FRONTEND_DIST = _BACKEND_DIR.parent / "frontend" / "dist" / "index.html"
_FRONTEND_DEV = "http://localhost:5173"


def _construir_servicios(data_dir: Path):
    """Instancia y wiring de todos los servicios de la aplicación."""
    from app.api.eventos import crear_emisor_nulo
    from app.services.comparador import ComparadorServicio
    from app.services.explorador import ExploradorServicio
    from app.services.historial import HistorialServicio
    from app.services.log import LogServicio
    from app.services.perfiles import PerfilServicio
    from app.services.reglas import ReglasServicio
    from app.services.sincronizador import SincronizadorServicio
    from app.services.validador import ValidadorServicio
    from app.storage.config_storage import ConfigStorage
    from app.storage.historial_storage import HistorialStorage
    from app.storage.pending_storage import PendingSyncStorage
    from app.api.registro import Servicios

    config_storage = ConfigStorage(data_dir)
    historial_storage = HistorialStorage(data_dir)
    pending_storage = PendingSyncStorage(data_dir)

    log_servicio = LogServicio(callback=crear_emisor_nulo())
    explorador_servicio = ExploradorServicio()
    reglas_servicio = ReglasServicio(config_storage)
    perfil_servicio = PerfilServicio(config_storage)
    comparador_servicio = ComparadorServicio(explorador_servicio)
    validador_servicio = ValidadorServicio(config_storage)
    sincronizador_servicio = SincronizadorServicio(pending_storage, log_servicio)
    historial_servicio = HistorialServicio(historial_storage, config_storage)

    return Servicios(
        config_storage=config_storage,
        perfil_servicio=perfil_servicio,
        reglas_servicio=reglas_servicio,
        validador_servicio=validador_servicio,
        comparador_servicio=comparador_servicio,
        sincronizador_servicio=sincronizador_servicio,
        historial_servicio=historial_servicio,
        log_servicio=log_servicio,
    )


class Api:
    """
    Objeto API expuesto a JavaScript por pywebview.

    Pywebview refleja cada método público como ``window.pywebview.api.<metodo>()``.
    """

    def __init__(self, dispatcher) -> None:
        self._dispatcher = dispatcher

    def despachar(self, json_str: str) -> str:
        """Recibe y despachada una llamada JSON-RPC 2.0."""
        return self._dispatcher.despachar(json_str)


def main(dev: bool = False) -> None:
    """
    Punto de entrada principal.

    Args:
        dev: Si es ``True`` conecta al servidor de desarrollo de Vite en lugar
             de cargar el bundle compilado.
    """
    import webview  # type: ignore[import-untyped]
    from app.api.dispatcher import Dispatcher
    from app.api.eventos import crear_emisor_evento
    from app.api.registro import registrar_todos

    servicios = _construir_servicios(_DATA_DIR)
    dispatcher = Dispatcher()

    # Crear ventana (window disponible tras webview.start)
    url = _FRONTEND_DEV if dev else _FRONTEND_DIST.as_uri()

    api = Api(dispatcher)
    window = webview.create_window(
        title="Sincroniza",
        url=url,
        js_api=api,
        width=1280,
        height=800,
        min_size=(800, 600),
    )

    def on_loaded() -> None:
        """Conecta el emisor de eventos tras cargar el frontend."""
        emisor = crear_emisor_evento(window)
        servicios.log_servicio.establecer_callback(emisor)
        registrar_todos(dispatcher, servicios, window)

    webview.start(on_loaded, debug=dev)


if __name__ == "__main__":
    dev_mode = "--dev" in sys.argv
    main(dev=dev_mode)
