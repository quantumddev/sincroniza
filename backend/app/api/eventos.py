"""
Eventos push — mecanismo de notificación backend → frontend.

El backend envía eventos al frontend usando ``window.evaluate_js()`` de
pywebview, lo que invoca el callback global ``window.__sincroniza_evento``
registrado por el frontend.

Ref: §04_protocolo_jsonrpc.md — «Eventos push»
"""

from __future__ import annotations

import json
from typing import Callable

from app.models.evento_log import EventoLog


def crear_emisor_evento(window: object) -> Callable[[EventoLog], None]:
    """
    Crea una función que emite un ``EventoLog`` al frontend.

    La función resultante serializa el evento a JSON y llama a
    ``window.__sincroniza_evento`` mediante ``window.evaluate_js()``.

    Args:
        window: Instancia de la ventana pywebview. Debe exponer
                ``evaluate_js(js: str)`` para inyectar código en el frontend.

    Returns:
        Callable que acepta un ``EventoLog`` y lo envía al frontend.
    """
    def emitir(evento: EventoLog) -> None:
        evento_json = json.dumps(evento.to_dict(), ensure_ascii=False)
        # Escapar comillas simples para incrustar en el literal JS
        evento_json_escaped = evento_json.replace("\\", "\\\\").replace("'", "\\'")
        js = f"window.__sincroniza_evento('{evento_json_escaped}')"
        try:
            window.evaluate_js(js)  # type: ignore[union-attr]
        except Exception:  # noqa: BLE001
            # Si el frontend no está disponible aún, descartamos el evento sin
            # interrumpir el hilo worker.
            pass

    return emitir


def crear_emisor_nulo() -> Callable[[EventoLog], None]:
    """
    Crea un emisor que descarta todos los eventos sin efectos secundarios.

    Útil en tests o cuando no hay ventana pywebview disponible.
    """
    def _nulo(_evento: EventoLog) -> None:
        pass

    return _nulo
