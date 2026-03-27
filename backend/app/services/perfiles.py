"""
PerfilServicio — CRUD de perfiles de sincronización.

Gestiona la lista ``ConfiguracionApp.perfiles`` que persiste ``ConfigStorage``.
Genera UUIDs para los nuevos perfiles y delega toda la persistencia al storage.

Ref: §10
"""

from __future__ import annotations

import uuid

from app.core.fechas import timestamp_ahora
from app.models.enums import MetodoComparacion
from app.models.perfil import Perfil
from app.storage.config_storage import ConfigStorage


class PerfilServicio:
    """
    CRUD de perfiles de sincronización.

    Args:
        config_storage: ``ConfigStorage`` que contiene la lista de perfiles.
    """

    def __init__(self, config_storage: ConfigStorage) -> None:
        self._storage = config_storage

    # ── Lectura ───────────────────────────────────────────────────────────────

    def listar(self) -> list[Perfil]:
        """Retorna todos los perfiles almacenados."""
        return list(self._storage.leer().perfiles)

    def obtener(self, perfil_id: str) -> Perfil | None:
        """Retorna el perfil con el ``id`` dado, o ``None`` si no existe."""
        for perfil in self._storage.leer().perfiles:
            if perfil.id == perfil_id:
                return perfil
        return None

    # ── Escritura ─────────────────────────────────────────────────────────────

    def crear(
        self,
        nombre: str,
        origen: str,
        destino: str,
        *,
        metodo_comparacion: MetodoComparacion | None = None,
        reglas_exclusion_ids: list[str] | None = None,
        reglas_propias: list | None = None,
        umbral_eliminaciones: int | None = None,
        timeout_por_archivo: int | None = None,
    ) -> Perfil:
        """
        Crea un perfil nuevo con UUID generado y lo persiste.

        Los valores opcionales no provistos se toman de la configuración global.

        Returns:
            El ``Perfil`` recién creado.
        """
        config = self._storage.leer()

        perfil = Perfil(
            id=str(uuid.uuid4()),
            nombre=nombre,
            origen=origen,
            destino=destino,
            metodo_comparacion=(
                metodo_comparacion
                if metodo_comparacion is not None
                else config.metodo_comparacion_defecto
            ),
            reglas_exclusion_ids=reglas_exclusion_ids if reglas_exclusion_ids is not None else [],
            reglas_propias=reglas_propias if reglas_propias is not None else [],
            umbral_eliminaciones=(
                umbral_eliminaciones
                if umbral_eliminaciones is not None
                else config.umbral_eliminaciones
            ),
            timeout_por_archivo=(
                timeout_por_archivo
                if timeout_por_archivo is not None
                else config.timeout_por_archivo
            ),
            creado=timestamp_ahora(),
            ultima_ejecucion=None,
        )
        config.perfiles.append(perfil)
        self._storage.escribir(config)
        return perfil

    def actualizar(self, perfil_id: str, cambios: dict) -> Perfil:
        """
        Aplica ``cambios`` al perfil indicado y lo persiste.

        Raises:
            KeyError: Si el perfil no existe.
        """
        config = self._storage.leer()
        for i, perfil in enumerate(config.perfiles):
            if perfil.id == perfil_id:
                datos = perfil.to_dict()
                datos.update(cambios)
                nuevo = Perfil.from_dict(datos)
                config.perfiles[i] = nuevo
                self._storage.escribir(config)
                return nuevo
        raise KeyError(f"Perfil no encontrado: {perfil_id}")

    def eliminar(self, perfil_id: str) -> bool:
        """
        Elimina el perfil indicado.

        Returns:
            ``True`` si existía y fue eliminado, ``False`` si no existía.
        """
        config = self._storage.leer()
        for i, perfil in enumerate(config.perfiles):
            if perfil.id == perfil_id:
                config.perfiles.pop(i)
                self._storage.escribir(config)
                return True
        return False

    def actualizar_ultima_ejecucion(
        self,
        perfil_id: str,
        timestamp: str | None = None,
    ) -> Perfil:
        """
        Registra la marca de tiempo de la última ejecución del perfil.

        Si ``timestamp`` es ``None`` se usa la hora actual.

        Raises:
            KeyError: Si el perfil no existe.
        """
        ts = timestamp if timestamp is not None else timestamp_ahora()
        return self.actualizar(perfil_id, {"ultima_ejecucion": ts})
