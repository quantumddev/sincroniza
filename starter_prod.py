"""
starter_prod.py — Arranca Sincroniza en MODO PRODUCCIÓN.

Carga el bundle compilado desde frontend/dist/index.html.
Diseñado tanto para ejecución directa como para ser empaquetado con PyInstaller.

Uso::

    python starter_prod.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# ── Rutas ─────────────────────────────────────────────────────────────────────

# Dentro de PyInstaller los archivos se extraen en sys._MEIPASS
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys._MEIPASS)  # type: ignore[attr-defined]
else:
    BASE_DIR = Path(__file__).parent

FRONTEND_URL = (BASE_DIR / "frontend" / "dist" / "index.html").as_uri()

# Directorio de datos:
#   · ejecutable .exe → carpeta junto al propio .exe (persistente entre ejecuciones)
#   · ejecución normal → raíz del proyecto / data
if getattr(sys, "frozen", False):
    DATA_DIR = Path(sys.executable).parent / "data"
else:
    DATA_DIR = BASE_DIR / "data"

# Añadir backend/ al path → los imports son: «from app.xxx import ...»
sys.path.insert(0, str(BASE_DIR / "backend"))


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    import webview  # type: ignore[import-untyped]
    from main import Api, _construir_servicios  # noqa: PLC0415
    from app.api.dispatcher import Dispatcher  # noqa: PLC0415
    from app.api.eventos import crear_emisor_evento  # noqa: PLC0415
    from app.api.registro import registrar_todos  # noqa: PLC0415

    servicios = _construir_servicios(DATA_DIR)
    dispatcher = Dispatcher()
    api = Api(dispatcher)

    ventana = webview.create_window(
        title="Sincroniza",
        url=FRONTEND_URL,
        js_api=api,
        width=1280,
        height=800,
        min_size=(800, 600),
        maximized=True,
    )

    def on_loaded() -> None:
        emisor = crear_emisor_evento(ventana)
        servicios.log_servicio.establecer_callback(emisor)
        registrar_todos(dispatcher, servicios, ventana)

    def on_closing() -> bool:
        return bool(ventana.create_confirmation_dialog(
            "¿Cerrar Sincroniza?",
            "¿Deseas salir de la aplicación?",
        ))

    ventana.events.closing += on_closing

    webview.start(on_loaded, debug=False)


if __name__ == "__main__":
    main()
