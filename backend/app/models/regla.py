"""
Modelo Regla — patrón glob de exclusión.

Ref: §10
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Self

from app.models.enums import OrigenRegla, TipoRegla


@dataclass(frozen=True)
class Regla:
    """Regla de exclusión basada en un patrón glob."""

    id: str               # UUID v4
    patron: str           # Glob pattern (ej: "node_modules/**")
    tipo: TipoRegla       # Aplica a archivos, carpetas o ambos
    activa: bool          # Si la regla está habilitada
    origen: OrigenRegla   # Sistema (predefinida) o usuario (creada)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "patron": self.patron,
            "tipo": self.tipo.value,
            "activa": self.activa,
            "origen": self.origen.value,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(
            id=data["id"],
            patron=data["patron"],
            tipo=TipoRegla(data["tipo"]),
            activa=data["activa"],
            origen=OrigenRegla(data["origen"]),
        )
