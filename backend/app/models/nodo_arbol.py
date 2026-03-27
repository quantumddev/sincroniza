"""
Modelos de representación del filesystem y del árbol de diferencias.

Ref: §7, §14
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Self

from app.models.enums import EstadoNodo, TipoElemento


@dataclass(frozen=True)
class EntradaFilesystem:
    """Elemento detectado al explorar un directorio (resultado del explorador)."""

    ruta_relativa: str    # Ruta relativa al directorio raíz
    tipo: TipoElemento    # archivo, carpeta, symlink, otro
    tamaño: int           # Bytes (0 para carpetas)
    mtime: float          # Timestamp de última modificación (POSIX)
    es_oculto: bool       # Archivo/carpeta oculto del sistema
    es_symlink: bool      # Es enlace simbólico o junction

    def to_dict(self) -> dict:
        return {
            "ruta_relativa": self.ruta_relativa,
            "tipo": self.tipo.value,
            "tamaño": self.tamaño,
            "mtime": self.mtime,
            "es_oculto": self.es_oculto,
            "es_symlink": self.es_symlink,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(
            ruta_relativa=data["ruta_relativa"],
            tipo=TipoElemento(data["tipo"]),
            tamaño=data["tamaño"],
            mtime=data["mtime"],
            es_oculto=data["es_oculto"],
            es_symlink=data["es_symlink"],
        )


@dataclass
class NodoArbol:
    """Nodo jerárquico del árbol de diferencias producido por el comparador."""

    nombre: str                  # Nombre del archivo o carpeta
    ruta_relativa: str           # Ruta relativa completa desde la raíz
    tipo: TipoElemento           # archivo, carpeta, symlink, otro
    estado: EstadoNodo           # nuevo, modificado, eliminado, idéntico, etc.
    tamaño: int                  # Bytes en origen
    tamaño_destino: int | None   # Bytes en destino (None si no existe)
    motivo: str | None           # Motivo de exclusión, error o conflicto
    hijos: list[NodoArbol] = field(default_factory=list)  # Subnodos (vacío para archivos)

    def to_dict(self) -> dict:
        return {
            "nombre": self.nombre,
            "ruta_relativa": self.ruta_relativa,
            "tipo": self.tipo.value,
            "estado": self.estado.value,
            "tamaño": self.tamaño,
            "tamaño_destino": self.tamaño_destino,
            "motivo": self.motivo,
            "hijos": [h.to_dict() for h in self.hijos],
        }

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(
            nombre=data["nombre"],
            ruta_relativa=data["ruta_relativa"],
            tipo=TipoElemento(data["tipo"]),
            estado=EstadoNodo(data["estado"]),
            tamaño=data["tamaño"],
            tamaño_destino=data.get("tamaño_destino"),
            motivo=data.get("motivo"),
            hijos=[NodoArbol.from_dict(h) for h in data.get("hijos", [])],
        )
