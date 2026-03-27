"""
Modelo ResultadoEjecucion — resultado persistido de una sincronización.

Ref: §13.3
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Self

from app.models.enums import EstadoEjecucion, MetodoComparacion
from app.models.error import ErrorSincronizacion
from app.models.plan import OperacionPlanificada, ResumenPlan


@dataclass
class ResultadoEjecucion:
    """Registro persistido del resultado de ejecutar un plan de sincronización."""

    id: str                                       # UUID v4
    plan_id: str                                  # ID del plan que se ejecutó
    perfil_id: str                                # ID del perfil
    origen: str                                   # Ruta origen
    destino: str                                  # Ruta destino
    metodo_comparacion: MetodoComparacion
    reglas_activas: list[str]                     # IDs de reglas aplicadas
    estado: EstadoEjecucion                       # Estado final
    modo_prueba: bool                             # Si fue en modo dry-run
    resumen: ResumenPlan
    operaciones_completadas: list[OperacionPlanificada]
    operaciones_fallidas: list[OperacionPlanificada]
    errores: list[ErrorSincronizacion]
    reintentos: list[dict]                        # Registro de reintentos realizados
    duracion_analisis: float                      # Segundos que duró el análisis
    duracion_ejecucion: float                     # Segundos que duró la ejecución
    timestamp_inicio: str                         # ISO 8601
    timestamp_fin: str                            # ISO 8601
    version_esquema: int                          # Versión del formato JSON

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "plan_id": self.plan_id,
            "perfil_id": self.perfil_id,
            "origen": self.origen,
            "destino": self.destino,
            "metodo_comparacion": self.metodo_comparacion.value,
            "reglas_activas": list(self.reglas_activas),
            "estado": self.estado.value,
            "modo_prueba": self.modo_prueba,
            "resumen": self.resumen.to_dict(),
            "operaciones_completadas": [op.to_dict() for op in self.operaciones_completadas],
            "operaciones_fallidas": [op.to_dict() for op in self.operaciones_fallidas],
            "errores": [e.to_dict() for e in self.errores],
            "reintentos": list(self.reintentos),
            "duracion_analisis": self.duracion_analisis,
            "duracion_ejecucion": self.duracion_ejecucion,
            "timestamp_inicio": self.timestamp_inicio,
            "timestamp_fin": self.timestamp_fin,
            "version_esquema": self.version_esquema,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(
            id=data["id"],
            plan_id=data["plan_id"],
            perfil_id=data["perfil_id"],
            origen=data["origen"],
            destino=data["destino"],
            metodo_comparacion=MetodoComparacion(data["metodo_comparacion"]),
            reglas_activas=list(data["reglas_activas"]),
            estado=EstadoEjecucion(data["estado"]),
            modo_prueba=data["modo_prueba"],
            resumen=ResumenPlan.from_dict(data["resumen"]),
            operaciones_completadas=[
                OperacionPlanificada.from_dict(op) for op in data["operaciones_completadas"]
            ],
            operaciones_fallidas=[
                OperacionPlanificada.from_dict(op) for op in data["operaciones_fallidas"]
            ],
            errores=[ErrorSincronizacion.from_dict(e) for e in data["errores"]],
            reintentos=list(data["reintentos"]),
            duracion_analisis=data["duracion_analisis"],
            duracion_ejecucion=data["duracion_ejecucion"],
            timestamp_inicio=data["timestamp_inicio"],
            timestamp_fin=data["timestamp_fin"],
            version_esquema=data["version_esquema"],
        )
