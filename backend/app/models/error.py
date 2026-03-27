"""
Modelo ErrorSincronizacion — error ocurrido durante análisis o ejecución.

Ref: §12
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Self

from app.models.enums import FaseOperacion


@dataclass(frozen=True)
class ErrorSincronizacion:
    """Error ocurrido durante el análisis o la ejecución de la sincronización."""

    codigo: str               # Código de error (ej: "PERMISO_DENEGADO")
    mensaje: str              # Descripción legible del error
    ruta: str                 # Ruta afectada por el error
    fase: FaseOperacion       # Fase en que ocurrió: análisis o ejecución
    recuperable: bool         # Si la operación puede reintentarse
    timestamp: str            # ISO 8601

    def to_dict(self) -> dict:
        return {
            "codigo": self.codigo,
            "mensaje": self.mensaje,
            "ruta": self.ruta,
            "fase": self.fase.value,
            "recuperable": self.recuperable,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(
            codigo=data["codigo"],
            mensaje=data["mensaje"],
            ruta=data["ruta"],
            fase=FaseOperacion(data["fase"]),
            recuperable=data["recuperable"],
            timestamp=data["timestamp"],
        )
