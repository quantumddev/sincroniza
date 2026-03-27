"""
ComparadorServicio — Motor de análisis de diferencias entre origen y destino.

Compara dos árboles de filesystem explorados por ``ExploradorServicio``
y produce un ``PlanSincronizacion`` con todas las operaciones necesarias.

Ref: §11, §12
"""

from __future__ import annotations

import os
import re
import uuid

from app.core.fechas import obtener_mtime, timestamp_ahora
from app.core.fingerprint import calcular_fingerprint
from app.core.glob_matcher import evaluar_reglas
from app.core.hashing import calcular_hash_archivo
from app.models.enums import (
    EstadoNodo,
    MetodoComparacion,
    TipoElemento,
    TipoOperacion,
)
from app.models.nodo_arbol import EntradaFilesystem, NodoArbol
from app.models.perfil import Perfil
from app.models.plan import (
    OperacionPlanificada,
    PlanSincronizacion,
    ResumenPlan,
)
from app.models.regla import Regla
from app.services.explorador import ExploradorServicio

# Patrón para detectar archivos en conflicto de nubes (OneDrive, Dropbox…)
_RE_CONFLICTO_NUBE = re.compile(r"conflicto", re.IGNORECASE)


class ComparadorServicio:
    """
    Analiza diferencias entre dos directorios y construye un plan de sincronización.

    Args:
        explorador: Instancia de ``ExploradorServicio`` usada para explorar los
                    directorios de origen y destino.
    """

    def __init__(self, explorador: ExploradorServicio) -> None:
        self._explorador = explorador

    # ── Pública ───────────────────────────────────────────────────────────────

    def analizar(
        self,
        origen: str,
        destino: str,
        perfil: Perfil,
        reglas: list[Regla],
    ) -> PlanSincronizacion:
        """
        Explora origen y destino y devuelve un ``PlanSincronizacion`` completo.

        Args:
            origen:  Ruta absoluta del directorio origen.
            destino: Ruta absoluta del directorio destino.
            perfil:  Perfil de sincronización activo.
            reglas:  Lista de reglas de exclusión a aplicar.

        Returns:
            `PlanSincronizacion` listo para ser ejecutado o revisado.
        """
        entradas_origen = self._explorador.explorar(origen)
        entradas_destino = self._explorador.explorar(destino)

        mtime_origen = obtener_mtime(origen) or 0.0
        mtime_destino = obtener_mtime(destino) or 0.0

        # Índices por ruta relativa para búsquedas O(1)
        idx_origen: dict[str, EntradaFilesystem] = {
            e.ruta_relativa: e for e in entradas_origen
        }
        idx_destino: dict[str, EntradaFilesystem] = {
            e.ruta_relativa: e for e in entradas_destino
        }

        # IDs de reglas activas para el fingerprint
        reglas_activas_ids = [r.id for r in reglas if r.activa]

        # Clasificar cada entrada
        nodos: list[NodoArbol] = []
        operaciones: list[OperacionPlanificada] = []

        # Entradas presentes en origen (nuevas / modificadas / idénticas / excluidas)
        for ruta_rel, e_orig in idx_origen.items():
            nodo, op = self._clasificar_entrada_origen(
                ruta_rel, e_orig, idx_destino, origen, destino, perfil, reglas
            )
            nodos.append(nodo)
            if op is not None:
                operaciones.append(op)

        # Entradas sólo en destino (eliminadas)
        for ruta_rel, e_dst in idx_destino.items():
            if ruta_rel not in idx_origen:
                nodo, op = self._clasificar_eliminado(
                    ruta_rel, e_dst, destino, reglas
                )
                nodos.append(nodo)
                if op is not None:
                    operaciones.append(op)

        resumen = self._calcular_resumen(nodos, operaciones)
        arbol = self._construir_arbol(nodos)
        fingerprint = calcular_fingerprint(
            origen, destino, reglas_activas_ids, perfil.metodo_comparacion
        )

        return PlanSincronizacion(
            id=str(uuid.uuid4()),
            perfil_id=perfil.id,
            origen=origen,
            destino=destino,
            metodo_comparacion=perfil.metodo_comparacion,
            reglas_activas=reglas_activas_ids,
            arbol=arbol,
            operaciones=operaciones,
            resumen=resumen,
            fingerprint=fingerprint,
            mtime_origen=mtime_origen,
            mtime_destino=mtime_destino,
            timestamp=timestamp_ahora(),
        )

    # ── Clasificación de entradas ─────────────────────────────────────────────

    def _clasificar_entrada_origen(
        self,
        ruta_rel: str,
        e_orig: EntradaFilesystem,
        idx_destino: dict[str, EntradaFilesystem],
        origen: str,
        destino: str,
        perfil: Perfil,
        reglas: list[Regla],
    ) -> tuple[NodoArbol, OperacionPlanificada | None]:
        nombre = os.path.basename(ruta_rel)
        es_carpeta = e_orig.tipo == TipoElemento.CARPETA

        # Conflicto de nube
        if _RE_CONFLICTO_NUBE.search(nombre):
            nodo = NodoArbol(
                nombre=nombre,
                ruta_relativa=ruta_rel,
                tipo=e_orig.tipo,
                estado=EstadoNodo.CONFLICTO_NUBE,
                tamaño=e_orig.tamaño,
                tamaño_destino=None,
                motivo="Detectado conflicto de sincronización en nube",
            )
            return nodo, None

        # Excluida por regla
        regla = evaluar_reglas(reglas, ruta_rel, es_carpeta)
        if regla is not None:
            nodo = NodoArbol(
                nombre=nombre,
                ruta_relativa=ruta_rel,
                tipo=e_orig.tipo,
                estado=EstadoNodo.EXCLUIDO,
                tamaño=e_orig.tamaño,
                tamaño_destino=None,
                motivo=f"Excluida por regla: {regla.patron}",
            )
            return nodo, None

        e_dst = idx_destino.get(ruta_rel)

        if e_dst is None:
            # Elemento nuevo en origen
            estado = EstadoNodo.NUEVO
            op = self._op_nuevo(e_orig, ruta_rel, origen, destino)
            nodo = NodoArbol(
                nombre=nombre,
                ruta_relativa=ruta_rel,
                tipo=e_orig.tipo,
                estado=estado,
                tamaño=e_orig.tamaño,
                tamaño_destino=None,
                motivo=None,
            )
            return nodo, op

        # Elemento presente en ambos lados
        if es_carpeta:
            # Las carpetas existentes no generan operación
            nodo = NodoArbol(
                nombre=nombre,
                ruta_relativa=ruta_rel,
                tipo=e_orig.tipo,
                estado=EstadoNodo.IDENTICO,
                tamaño=e_orig.tamaño,
                tamaño_destino=e_dst.tamaño,
                motivo=None,
            )
            return nodo, None

        # Comparar archivo
        modificado = self._esta_modificado(e_orig, e_dst, origen, destino, ruta_rel, perfil)
        if modificado:
            estado = EstadoNodo.MODIFICADO
            ruta_origen_abs = os.path.join(origen, ruta_rel)
            ruta_destino_abs = os.path.join(destino, ruta_rel)
            op = OperacionPlanificada(
                tipo=TipoOperacion.REEMPLAZAR,
                ruta_origen=ruta_origen_abs,
                ruta_destino=ruta_destino_abs,
                ruta_relativa=ruta_rel,
                tamaño=e_orig.tamaño,
            )
        else:
            estado = EstadoNodo.IDENTICO
            op = None

        nodo = NodoArbol(
            nombre=nombre,
            ruta_relativa=ruta_rel,
            tipo=e_orig.tipo,
            estado=estado,
            tamaño=e_orig.tamaño,
            tamaño_destino=e_dst.tamaño,
            motivo=None,
        )
        return nodo, op

    def _clasificar_eliminado(
        self,
        ruta_rel: str,
        e_dst: EntradaFilesystem,
        destino: str,
        reglas: list[Regla],
    ) -> tuple[NodoArbol, OperacionPlanificada | None]:
        nombre = os.path.basename(ruta_rel)
        es_carpeta = e_dst.tipo == TipoElemento.CARPETA

        # Excluida por regla → no eliminar
        if evaluar_reglas(reglas, ruta_rel, es_carpeta) is not None:
            nodo = NodoArbol(
                nombre=nombre,
                ruta_relativa=ruta_rel,
                tipo=e_dst.tipo,
                estado=EstadoNodo.EXCLUIDO,
                tamaño=0,
                tamaño_destino=e_dst.tamaño,
                motivo="Excluida: solo en destino",
            )
            return nodo, None

        ruta_destino_abs = os.path.join(destino, ruta_rel)
        tipo_op = (
            TipoOperacion.ELIMINAR_CARPETA
            if es_carpeta
            else TipoOperacion.ELIMINAR_ARCHIVO
        )
        op = OperacionPlanificada(
            tipo=tipo_op,
            ruta_origen=None,
            ruta_destino=ruta_destino_abs,
            ruta_relativa=ruta_rel,
            tamaño=e_dst.tamaño,
        )
        nodo = NodoArbol(
            nombre=nombre,
            ruta_relativa=ruta_rel,
            tipo=e_dst.tipo,
            estado=EstadoNodo.ELIMINADO,
            tamaño=0,
            tamaño_destino=e_dst.tamaño,
            motivo=None,
        )
        return nodo, op

    # ── Comparación de archivos ───────────────────────────────────────────────

    def _esta_modificado(
        self,
        e_orig: EntradaFilesystem,
        e_dst: EntradaFilesystem,
        origen: str,
        destino: str,
        ruta_rel: str,
        perfil: Perfil,
    ) -> bool:
        if perfil.metodo_comparacion == MetodoComparacion.HASH:
            try:
                hash_orig = calcular_hash_archivo(os.path.join(origen, ruta_rel))
                hash_dst = calcular_hash_archivo(os.path.join(destino, ruta_rel))
                return hash_orig != hash_dst
            except OSError:
                return True
        # TAMAÑO_FECHA (predeterminado)
        return e_orig.tamaño != e_dst.tamaño or e_orig.mtime != e_dst.mtime

    # ── Operaciones para elementos nuevos ─────────────────────────────────────

    def _op_nuevo(
        self,
        e_orig: EntradaFilesystem,
        ruta_rel: str,
        origen: str,
        destino: str,
    ) -> OperacionPlanificada | None:
        ruta_origen_abs = os.path.join(origen, ruta_rel)
        ruta_destino_abs = os.path.join(destino, ruta_rel)

        if e_orig.tipo == TipoElemento.CARPETA:
            return OperacionPlanificada(
                tipo=TipoOperacion.CREAR_CARPETA,
                ruta_origen=None,
                ruta_destino=ruta_destino_abs,
                ruta_relativa=ruta_rel,
                tamaño=0,
            )
        if e_orig.tipo == TipoElemento.ARCHIVO:
            return OperacionPlanificada(
                tipo=TipoOperacion.COPIAR,
                ruta_origen=ruta_origen_abs,
                ruta_destino=ruta_destino_abs,
                ruta_relativa=ruta_rel,
                tamaño=e_orig.tamaño,
            )
        # Symlinks y otros tipos no se sincronizan
        return None

    # ── Construcción del árbol y resumen ─────────────────────────────────────

    def _construir_arbol(self, nodos: list[NodoArbol]) -> NodoArbol:
        """
        Construye un nodo raíz con todos los nodos como hijos directos.

        No implementa jerarquía completa interna (responsabilidad de la UI).
        """
        return NodoArbol(
            nombre="",
            ruta_relativa="",
            tipo=TipoElemento.CARPETA,
            estado=EstadoNodo.IDENTICO,
            tamaño=0,
            tamaño_destino=0,
            motivo=None,
            hijos=list(nodos),
        )

    def _calcular_resumen(
        self,
        nodos: list[NodoArbol],
        operaciones: list[OperacionPlanificada],
    ) -> ResumenPlan:
        contadores: dict[EstadoNodo, int] = {e: 0 for e in EstadoNodo}
        for nodo in nodos:
            contadores[nodo.estado] = contadores.get(nodo.estado, 0) + 1

        tamaño_copiar = sum(
            op.tamaño
            for op in operaciones
            if op.tipo == TipoOperacion.COPIAR
        )
        tamaño_reemplazar = sum(
            op.tamaño
            for op in operaciones
            if op.tipo == TipoOperacion.REEMPLAZAR
        )
        tamaño_eliminar = sum(
            op.tamaño
            for op in operaciones
            if op.tipo in (TipoOperacion.ELIMINAR_ARCHIVO, TipoOperacion.ELIMINAR_CARPETA)
        )

        return ResumenPlan(
            nuevos=contadores[EstadoNodo.NUEVO],
            modificados=contadores[EstadoNodo.MODIFICADO],
            eliminados=contadores[EstadoNodo.ELIMINADO],
            identicos=contadores[EstadoNodo.IDENTICO],
            excluidos=contadores[EstadoNodo.EXCLUIDO],
            errores=contadores[EstadoNodo.ERROR],
            conflictos_nube=contadores[EstadoNodo.CONFLICTO_NUBE],
            omitidos=contadores[EstadoNodo.OMITIDO],
            tamaño_copiar=tamaño_copiar,
            tamaño_reemplazar=tamaño_reemplazar,
            tamaño_eliminar=tamaño_eliminar,
            total_elementos=len(nodos),
        )
