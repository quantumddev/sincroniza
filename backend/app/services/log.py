"""
LogServicio — acumulación y emisión de eventos de log.

Genera ``EventoLog`` con timestamp automático, los acumula en memoria
y los propaga a un callback opcional para push en tiempo real hacia la UI.

Ref: §15
"""

from __future__ import annotations

from typing import Callable

from app.core.fechas import timestamp_ahora
from app.models.enums import NivelLog
from app.models.evento_log import EventoLog


class LogServicio:
    """
    Servicio de log del backend.

    Args:
        callback: Función que recibe cada ``EventoLog`` en tiempo real.
                  Puede ser ``None`` (modo silencioso).
    """

    def __init__(self, callback: Callable[[EventoLog], None] | None = None) -> None:
        self._eventos: list[EventoLog] = []
        self._callback = callback

    # ── API pública ───────────────────────────────────────────────────────────

    def info(
        self,
        tipo: str,
        mensaje: str,
        datos: dict | None = None,
    ) -> EventoLog:
        """Emite un evento de nivel INFO."""
        return self._emitir(tipo, NivelLog.INFO, mensaje, datos)

    def warning(
        self,
        tipo: str,
        mensaje: str,
        datos: dict | None = None,
    ) -> EventoLog:
        """Emite un evento de nivel WARNING."""
        return self._emitir(tipo, NivelLog.WARNING, mensaje, datos)

    def error(
        self,
        tipo: str,
        mensaje: str,
        datos: dict | None = None,
    ) -> EventoLog:
        """Emite un evento de nivel ERROR."""
        return self._emitir(tipo, NivelLog.ERROR, mensaje, datos)

    def obtener_todos(self) -> list[EventoLog]:
        """Retorna copia de todos los eventos acumulados (más antiguo primero)."""
        return list(self._eventos)

    def vaciar(self) -> None:
        """Borra todos los eventos acumulados en memoria."""
        self._eventos.clear()

    def contar(self) -> int:
        """Número total de eventos acumulados."""
        return len(self._eventos)

    def establecer_callback(
        self, callback: Callable[[EventoLog], None] | None
    ) -> None:
        """Reemplaza el callback de push en tiempo real."""
        self._callback = callback

    # ── impl ──────────────────────────────────────────────────────────────────

    def _emitir(
        self,
        tipo: str,
        nivel: NivelLog,
        mensaje: str,
        datos: dict | None,
    ) -> EventoLog:
        evento = EventoLog(
            tipo=tipo,
            nivel=nivel,
            mensaje=mensaje,
            datos=datos,
            timestamp=timestamp_ahora(),
        )
        self._eventos.append(evento)
        if self._callback is not None:
            self._callback(evento)
        return evento
