"""
Modelos de configuración: ConfiguracionApp y PendingSync.

Ref: §13.2, §6.5
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Self

from app.models.enums import MetodoComparacion
from app.models.perfil import Perfil
from app.models.regla import Regla


@dataclass
class ConfiguracionApp:
    """Refleja el contenido completo de data/settings.json."""

    version_esquema: int
    tema: str                               # "claro" o "oscuro"
    metodo_comparacion_defecto: MetodoComparacion
    ultimas_rutas: dict                     # {"origen": str|None, "destino": str|None}
    perfiles: list[Perfil]
    reglas_exclusion: list[Regla]
    restricciones_ruta: dict                # {"origen_permitido": list[str], "destino_permitido": list[str]}
    umbral_eliminaciones: int
    timeout_por_archivo: int
    limite_historial: int

    def to_dict(self) -> dict:
        return {
            "version_esquema": self.version_esquema,
            "tema": self.tema,
            "metodo_comparacion_defecto": self.metodo_comparacion_defecto.value,
            "ultimas_rutas": dict(self.ultimas_rutas),
            "perfiles": [p.to_dict() for p in self.perfiles],
            "reglas_exclusion": [r.to_dict() for r in self.reglas_exclusion],
            "restricciones_ruta": dict(self.restricciones_ruta),
            "umbral_eliminaciones": self.umbral_eliminaciones,
            "timeout_por_archivo": self.timeout_por_archivo,
            "limite_historial": self.limite_historial,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(
            version_esquema=data["version_esquema"],
            tema=data["tema"],
            metodo_comparacion_defecto=MetodoComparacion(data["metodo_comparacion_defecto"]),
            ultimas_rutas=dict(data["ultimas_rutas"]),
            perfiles=[Perfil.from_dict(p) for p in data["perfiles"]],
            reglas_exclusion=[Regla.from_dict(r) for r in data["reglas_exclusion"]],
            restricciones_ruta=dict(data["restricciones_ruta"]),
            umbral_eliminaciones=data["umbral_eliminaciones"],
            timeout_por_archivo=data["timeout_por_archivo"],
            limite_historial=data["limite_historial"],
        )


@dataclass
class PendingSync:
    """
    Archivo temporal que registra una sincronización interrumpida,
    permitiendo detectar un crash y ofrecer recuperación al usuario.

    Ref: §6.5
    """

    plan_id: str
    perfil_id: str
    timestamp_inicio: str                   # ISO 8601
    operaciones_completadas: list[str]      # Rutas relativas ya procesadas
    operaciones_pendientes: list[str]       # Rutas relativas por procesar

    def to_dict(self) -> dict:
        return {
            "plan_id": self.plan_id,
            "perfil_id": self.perfil_id,
            "timestamp_inicio": self.timestamp_inicio,
            "operaciones_completadas": list(self.operaciones_completadas),
            "operaciones_pendientes": list(self.operaciones_pendientes),
        }

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(
            plan_id=data["plan_id"],
            perfil_id=data["perfil_id"],
            timestamp_inicio=data["timestamp_inicio"],
            operaciones_completadas=list(data["operaciones_completadas"]),
            operaciones_pendientes=list(data["operaciones_pendientes"]),
        )
