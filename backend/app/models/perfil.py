"""
Modelo Perfil — configuración de un par origen/destino.

Ref: §13.4
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Self

from app.models.enums import MetodoComparacion
from app.models.regla import Regla


@dataclass
class Perfil:
    """Configuración completa de una tarea de sincronización."""

    id: str                             # UUID v4
    nombre: str                         # Nombre descriptivo
    origen: str                         # Ruta absoluta del directorio origen
    destino: str                        # Ruta absoluta del directorio destino
    metodo_comparacion: MetodoComparacion
    reglas_exclusion_ids: list[str]     # IDs de reglas globales a usar
    reglas_propias: list[Regla]         # Reglas adicionales del perfil
    umbral_eliminaciones: int           # Máximo de eliminaciones sin advertencia
    timeout_por_archivo: int            # Segundos máximo por operación
    creado: str                         # ISO 8601
    ultima_ejecucion: str | None        # ISO 8601 o None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "origen": self.origen,
            "destino": self.destino,
            "metodo_comparacion": self.metodo_comparacion.value,
            "reglas_exclusion_ids": list(self.reglas_exclusion_ids),
            "reglas_propias": [r.to_dict() for r in self.reglas_propias],
            "umbral_eliminaciones": self.umbral_eliminaciones,
            "timeout_por_archivo": self.timeout_por_archivo,
            "creado": self.creado,
            "ultima_ejecucion": self.ultima_ejecucion,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(
            id=data["id"],
            nombre=data["nombre"],
            origen=data["origen"],
            destino=data["destino"],
            metodo_comparacion=MetodoComparacion(data["metodo_comparacion"]),
            reglas_exclusion_ids=list(data["reglas_exclusion_ids"]),
            reglas_propias=[Regla.from_dict(r) for r in data["reglas_propias"]],
            umbral_eliminaciones=data["umbral_eliminaciones"],
            timeout_por_archivo=data["timeout_por_archivo"],
            creado=data["creado"],
            ultima_ejecucion=data.get("ultima_ejecucion"),
        )
