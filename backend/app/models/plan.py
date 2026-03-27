"""
Modelos del plan de sincronización: operaciones, resumen y plan completo.

Ref: §6.1, §6.3, §8
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Self

from app.models.enums import MetodoComparacion, TipoOperacion
from app.models.nodo_arbol import NodoArbol


@dataclass(frozen=True)
class OperacionPlanificada:
    """Operación concreta que el sincronizador ejecutará sobre el destino."""

    tipo: TipoOperacion         # copiar, reemplazar, eliminar archivo, etc.
    ruta_origen: str | None     # Ruta absoluta en origen (None para eliminaciones)
    ruta_destino: str           # Ruta absoluta en destino
    ruta_relativa: str          # Ruta relativa para mostrar en la UI
    tamaño: int                 # Bytes involucrados en la operación

    def to_dict(self) -> dict:
        return {
            "tipo": self.tipo.value,
            "ruta_origen": self.ruta_origen,
            "ruta_destino": self.ruta_destino,
            "ruta_relativa": self.ruta_relativa,
            "tamaño": self.tamaño,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(
            tipo=TipoOperacion(data["tipo"]),
            ruta_origen=data.get("ruta_origen"),
            ruta_destino=data["ruta_destino"],
            ruta_relativa=data["ruta_relativa"],
            tamaño=data["tamaño"],
        )


@dataclass(frozen=True)
class ResumenPlan:
    """Resumen numérico del plan de sincronización."""

    nuevos: int
    modificados: int
    eliminados: int
    identicos: int
    excluidos: int
    errores: int
    conflictos_nube: int
    omitidos: int
    tamaño_copiar: int       # Bytes a copiar (archivos nuevos)
    tamaño_reemplazar: int   # Bytes a reemplazar (archivos modificados)
    tamaño_eliminar: int     # Bytes a eliminar
    total_elementos: int     # Total de elementos analizados

    def to_dict(self) -> dict:
        return {
            "nuevos": self.nuevos,
            "modificados": self.modificados,
            "eliminados": self.eliminados,
            "identicos": self.identicos,
            "excluidos": self.excluidos,
            "errores": self.errores,
            "conflictos_nube": self.conflictos_nube,
            "omitidos": self.omitidos,
            "tamaño_copiar": self.tamaño_copiar,
            "tamaño_reemplazar": self.tamaño_reemplazar,
            "tamaño_eliminar": self.tamaño_eliminar,
            "total_elementos": self.total_elementos,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(
            nuevos=data["nuevos"],
            modificados=data["modificados"],
            eliminados=data["eliminados"],
            identicos=data["identicos"],
            excluidos=data["excluidos"],
            errores=data["errores"],
            conflictos_nube=data["conflictos_nube"],
            omitidos=data["omitidos"],
            tamaño_copiar=data["tamaño_copiar"],
            tamaño_reemplazar=data["tamaño_reemplazar"],
            tamaño_eliminar=data["tamaño_eliminar"],
            total_elementos=data["total_elementos"],
        )


@dataclass
class PlanSincronizacion:
    """Resultado completo de un análisis de diferencias entre origen y destino."""

    id: str                              # UUID v4
    perfil_id: str                       # ID del perfil usado
    origen: str                          # Ruta origen analizada
    destino: str                         # Ruta destino analizada
    metodo_comparacion: MetodoComparacion
    reglas_activas: list[str]            # IDs de reglas aplicadas
    arbol: NodoArbol                     # Árbol jerárquico de diferencias
    operaciones: list[OperacionPlanificada]
    resumen: ResumenPlan
    fingerprint: str                     # Hash del plan para detección de desfase
    mtime_origen: float                  # mtime del directorio raíz origen al analizar
    mtime_destino: float                 # mtime del directorio raíz destino al analizar
    timestamp: str                       # ISO 8601 del momento del análisis

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "perfil_id": self.perfil_id,
            "origen": self.origen,
            "destino": self.destino,
            "metodo_comparacion": self.metodo_comparacion.value,
            "reglas_activas": list(self.reglas_activas),
            "arbol": self.arbol.to_dict(),
            "operaciones": [op.to_dict() for op in self.operaciones],
            "resumen": self.resumen.to_dict(),
            "fingerprint": self.fingerprint,
            "mtime_origen": self.mtime_origen,
            "mtime_destino": self.mtime_destino,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(
            id=data["id"],
            perfil_id=data["perfil_id"],
            origen=data["origen"],
            destino=data["destino"],
            metodo_comparacion=MetodoComparacion(data["metodo_comparacion"]),
            reglas_activas=list(data["reglas_activas"]),
            arbol=NodoArbol.from_dict(data["arbol"]),
            operaciones=[OperacionPlanificada.from_dict(op) for op in data["operaciones"]],
            resumen=ResumenPlan.from_dict(data["resumen"]),
            fingerprint=data["fingerprint"],
            mtime_origen=data["mtime_origen"],
            mtime_destino=data["mtime_destino"],
            timestamp=data["timestamp"],
        )
