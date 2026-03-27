"""
Modelo EventoLog — evento emitido durante análisis o ejecución hacia la UI.

Ref: §5, §15
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Self

from app.models.enums import NivelLog


@dataclass(frozen=True)
class EventoLog:
    """Evento de log emitido por el backend y enviado al frontend via push."""

    tipo: str              # Tipo de evento (catálogo en 04_protocolo_jsonrpc.md)
    nivel: NivelLog        # Severidad: info, warning, error
    mensaje: str           # Texto legible para mostrar en la UI
    datos: dict | None     # Datos estructurados adicionales (puede ser None)
    timestamp: str         # ISO 8601

    def to_dict(self) -> dict:
        return {
            "tipo": self.tipo,
            "nivel": self.nivel.value,
            "mensaje": self.mensaje,
            "datos": self.datos,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(
            tipo=data["tipo"],
            nivel=NivelLog(data["nivel"]),
            mensaje=data["mensaje"],
            datos=data.get("datos"),
            timestamp=data["timestamp"],
        )
