"""
ReglasServicio — CRUD y evaluación de reglas de exclusión.

Gestiona las reglas glob almacenadas en ``ConfiguracionApp.reglas_exclusion``.
Las reglas del sistema (``OrigenRegla.SISTEMA``) no pueden eliminarse.

Ref: §10
"""

from __future__ import annotations

import fnmatch
import uuid

from app.core.glob_matcher import evaluar_reglas
from app.models.enums import OrigenRegla, TipoRegla
from app.models.regla import Regla
from app.storage.config_storage import ConfigStorage


class ReglasServicio:
    """
    CRUD de reglas de exclusión + evaluación glob.

    Args:
        config_storage: ``ConfigStorage`` que persiste las reglas.
    """

    def __init__(self, config_storage: ConfigStorage) -> None:
        self._storage = config_storage

    # ── Lectura ───────────────────────────────────────────────────────────────

    def listar(self) -> list[Regla]:
        """Retorna todas las reglas globales (sistema + usuario)."""
        return list(self._storage.leer().reglas_exclusion)

    def obtener(self, regla_id: str) -> Regla | None:
        """Retorna la regla con el ``id`` indicado, o ``None`` si no existe."""
        for regla in self._storage.leer().reglas_exclusion:
            if regla.id == regla_id:
                return regla
        return None

    # ── Escritura ─────────────────────────────────────────────────────────────

    def crear(
        self,
        patron: str,
        tipo: TipoRegla,
        activa: bool = True,
    ) -> Regla:
        """
        Crea una regla de usuario con un UUID generado.

        Raises:
            ValueError: Si el patrón glob es inválido (vacío o mal formado).
        """
        if not self.validar_patron(patron):
            raise ValueError(f"Patrón glob inválido: {patron!r}")

        regla = Regla(
            id=str(uuid.uuid4()),
            patron=patron,
            tipo=tipo,
            activa=activa,
            origen=OrigenRegla.USUARIO,
        )
        config = self._storage.leer()
        config.reglas_exclusion.append(regla)
        self._storage.escribir(config)
        return regla

    def actualizar(self, regla_id: str, cambios: dict) -> Regla:
        """
        Aplica ``cambios`` sobre la regla indicada y la persiste.

        Las claves de ``cambios`` deben coincidir con los campos de ``Regla``.

        Raises:
            KeyError: Si la regla no existe.
            ValueError: Si el nuevo patrón es inválido.
        """
        config = self._storage.leer()
        for i, regla in enumerate(config.reglas_exclusion):
            if regla.id == regla_id:
                datos = regla.to_dict()
                datos.update(cambios)
                if "patron" in cambios and not self.validar_patron(datos["patron"]):
                    raise ValueError(f"Patrón glob inválido: {datos['patron']!r}")
                nueva = Regla.from_dict(datos)
                config.reglas_exclusion[i] = nueva
                self._storage.escribir(config)
                return nueva
        raise KeyError(f"Regla no encontrada: {regla_id}")

    def eliminar(self, regla_id: str) -> bool:
        """
        Elimina una regla de usuario.

        Returns:
            ``True`` si la regla existía y fue eliminada.
            ``False`` si no existía.

        Raises:
            PermissionError: Si se intenta eliminar una regla del sistema.
        """
        config = self._storage.leer()
        for i, regla in enumerate(config.reglas_exclusion):
            if regla.id == regla_id:
                if regla.origen == OrigenRegla.SISTEMA:
                    raise PermissionError(
                        f"Las reglas del sistema no se pueden eliminar: {regla_id}"
                    )
                config.reglas_exclusion.pop(i)
                self._storage.escribir(config)
                return True
        return False

    # ── Evaluación ─────────────────────────────────────────────────────────────

    def evaluar(self, ruta_relativa: str, es_carpeta: bool) -> Regla | None:
        """
        Evalúa la ruta contra la lista de reglas activas.

        Retorna la primera regla activa que coincide, o ``None`` si ninguna lo hace.
        """
        reglas = self._storage.leer().reglas_exclusion
        return evaluar_reglas(reglas, ruta_relativa, es_carpeta)

    # ── Validación ────────────────────────────────────────────────────────────

    @staticmethod
    def validar_patron(patron: str) -> bool:
        """
        Verifica si ``patron`` es un glob sintácticamente válido y no vacío.

        Retorna ``True`` si el patrón es usable.
        """
        if not patron or not patron.strip():
            return False
        try:
            # Normalizar ** a * para que fnmatch.translate pueda compilarlo
            fnmatch.translate(patron.replace("**", "*"))
            return True
        except Exception:
            return False
