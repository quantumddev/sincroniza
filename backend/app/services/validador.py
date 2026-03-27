"""
ValidadorServicio — validaciones de rutas y coherencia del plan.

Agrupa todas las validaciones de negocio sobre rutas y planes de sincronización.
Recibe ``ConfigStorage`` como dependencia para leer las restricciones de ruta.

Ref: §11
"""

from __future__ import annotations

from app.core.fechas import obtener_mtime
from app.core.fingerprint import calcular_fingerprint
from app.core.validaciones import (
    ruta_anidada,
    rutas_iguales,
    validar_restricciones_opcionales,
    validar_ruta_existe,
)
from app.models.plan import PlanSincronizacion
from app.storage.config_storage import ConfigStorage


class ValidadorServicio:
    """
    Valida rutas de origen/destino y la coherencia de los planes de análisis.

    Args:
        config_storage: Instancia de ``ConfigStorage`` para leer la configuración.
    """

    def __init__(self, config_storage: ConfigStorage) -> None:
        self._storage = config_storage

    # ── Validación de rutas ───────────────────────────────────────────────────

    def validar_rutas(self, origen: str, destino: str) -> tuple[bool, list[str]]:
        """
        Ejecuta todas las validaciones de seguridad sobre el par origen/destino.

        Comprobaciones (en orden):
        1. Ambas rutas existen en el filesystem.
        2. Origen ≠ destino (misma ruta normalizada).
        3. Ninguna está anidada dentro de la otra.
        4. Ambas respetan las restricciones de ruta configuradas (si hay lista).

        Returns:
            ``(True, [])`` si todas las validaciones pasan.
            ``(False, [mensajes_de_error])`` si hay algún fallo.
        """
        errores: list[str] = []

        # Existencia
        if not validar_ruta_existe(origen):
            errores.append(f"La ruta de origen no existe: {origen}")
        if not validar_ruta_existe(destino):
            errores.append(f"La ruta de destino no existe: {destino}")

        # Igualdad
        if rutas_iguales(origen, destino):
            errores.append("Origen y destino no pueden ser la misma ruta.")

        # Anidamiento
        if ruta_anidada(destino, origen):
            errores.append("El destino está dentro del origen.")
        if ruta_anidada(origen, destino):
            errores.append("El origen está dentro del destino.")

        # Restricciones de lista blanca
        config = self._storage.leer()
        permitidos_origen = config.restricciones_ruta.get("origen_permitido", [])
        permitidos_destino = config.restricciones_ruta.get("destino_permitido", [])

        if permitidos_origen and not validar_restricciones_opcionales(
            origen, permitidos_origen
        ):
            errores.append("La ruta de origen no está en la lista de rutas permitidas.")
        if permitidos_destino and not validar_restricciones_opcionales(
            destino, permitidos_destino
        ):
            errores.append("La ruta de destino no está en la lista de rutas permitidas.")

        return len(errores) == 0, errores

    # ── Validación del plan ───────────────────────────────────────────────────

    def verificar_fingerprint(self, plan: PlanSincronizacion) -> bool:
        """
        Recalcula el fingerprint del plan y lo compara con el almacenado.

        Retorna ``False`` si los parámetros del plan (rutas, reglas, método)
        han cambiado desde el último análisis.
        """
        fp = calcular_fingerprint(
            plan.origen,
            plan.destino,
            plan.reglas_activas,
            plan.metodo_comparacion,
        )
        return fp == plan.fingerprint

    def verificar_mtime_raiz(self, plan: PlanSincronizacion) -> bool:
        """
        Comprueba que los directorios raíz no han sido modificados desde el análisis.

        Retorna ``False`` si el mtime de origen o destino ha cambiado, o si
        alguno ya no es accesible.
        """
        try:
            mtime_origen_actual = obtener_mtime(plan.origen)
            mtime_destino_actual = obtener_mtime(plan.destino)
        except OSError:
            return False

        return (
            mtime_origen_actual == plan.mtime_origen
            and mtime_destino_actual == plan.mtime_destino
        )
