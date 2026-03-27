"""
HistorialServicio — Gestión del historial de ejecuciones.

Guarda, lista, obtiene y elimina ``ResultadoEjecucion`` persistidos por
``HistorialStorage``. El límite de entradas se lee de ``ConfigStorage``.

Ref: §13.3
"""

from __future__ import annotations

from app.models.resultado import ResultadoEjecucion  # noqa: F401 (usado en obtener)
from app.storage.config_storage import ConfigStorage
from app.storage.historial_storage import HistorialStorage


class HistorialServicio:
    """
    Capa de servicio sobre ``HistorialStorage``.

    Añade paginación en ``listar()`` y consulta el límite de historial
    desde la configuración global.

    Args:
        historial_storage: Storage que persiste los resultados de ejecución.
        config_storage:    Storage de configuración global (para ``limite_historial``).
    """

    def __init__(
        self,
        historial_storage: HistorialStorage,
        config_storage: ConfigStorage,
    ) -> None:
        self._historial = historial_storage
        self._config = config_storage

    # ── Escritura ──────────────────────────────────────────────────────────────

    def guardar(self, resultado: ResultadoEjecucion) -> None:
        """
        Persiste ``resultado`` respetando el límite configurado.

        El límite se lee en el momento de la llamada, por lo que reflejará
        siempre el valor actual de la configuración.
        """
        limite = self._config.leer().limite_historial
        self._historial.guardar(resultado, limite)

    # ── Lectura ────────────────────────────────────────────────────────────────

    def listar(self, pagina: int = 1, limite: int = 20) -> dict:
        """
        Retorna una página del historial.

        Args:
            pagina: Número de página (1-indexado).
            limite: Elementos por página.

        Returns:
            Diccionario ``{"items": [...], "total": int}``.
        """
        todos = self._historial.listar()
        total = len(todos)
        inicio = (max(pagina, 1) - 1) * max(limite, 1)
        fin = inicio + max(limite, 1)
        items = todos[inicio:fin]

        return {"items": items, "total": total}

    def obtener(self, resultado_id: str) -> ResultadoEjecucion | None:
        """Retorna el resultado con el ``id`` dado, o ``None``."""
        return self._historial.obtener(resultado_id)

    def eliminar(self, resultado_id: str) -> bool:
        """
        Elimina la entrada indicada.

        Returns:
            ``True`` si existía y fue eliminada, ``False`` en caso contrario.
        """
        return self._historial.eliminar(resultado_id)
