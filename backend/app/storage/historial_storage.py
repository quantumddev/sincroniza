"""
HistorialStorage — persistencia de ejecuciones en ``data/history/``.

Cada ``ResultadoEjecucion`` se guarda como un archivo JSON independiente
con el nombre ``run_<id>.json``.

Cuando el número de archivos supera el límite configurado, se eliminan
automáticamente los registros más antiguos (ordenados por mtime del archivo).

Ref: §13.3, §13.5
"""

from __future__ import annotations

import json
from pathlib import Path

from app.models.resultado import ResultadoEjecucion

# Subdirectorio relativo a ``data/`` donde se almacenan los registros.
HISTORY_SUBDIR = "history"

# Prefijo del nombre de cada archivo de historial.
FILE_PREFIX = "run_"


class HistorialStorage:
    """
    Lee, escribe y rota archivos de historial en ``data/history/``.

    Args:
        data_dir: Ruta al directorio ``data/``.
    """

    def __init__(self, data_dir: Path) -> None:
        self._dir = data_dir / HISTORY_SUBDIR
        self._dir.mkdir(parents=True, exist_ok=True)

    # ── helpers ───────────────────────────────────────────────────────────────

    def _ruta_para(self, resultado_id: str) -> Path:
        """Retorna la ruta al archivo de un resultado concreto."""
        return self._dir / f"{FILE_PREFIX}{resultado_id}.json"

    def _listar_archivos(self) -> list[Path]:
        """
        Retorna todos los archivos de historial ordenados por mtime ascendente
        (más antiguo primero).
        """
        return sorted(
            self._dir.glob(f"{FILE_PREFIX}*.json"),
            key=lambda p: p.stat().st_mtime,
        )

    def _rotar(self, limite: int) -> None:
        """
        Elimina los registros más antiguos si el total supera ``limite``.

        Un valor de ``limite <= 0`` deshabilita la rotación.
        """
        if limite <= 0:
            return
        archivos = self._listar_archivos()
        exceso = len(archivos) - limite
        if exceso <= 0:
            return
        for archivo in archivos[:exceso]:
            archivo.unlink(missing_ok=True)

    # ── API pública ───────────────────────────────────────────────────────────

    def guardar(self, resultado: ResultadoEjecucion, limite: int = 0) -> None:
        """
        Persiste el resultado y aplica rotación si se supera ``limite``.

        Args:
            resultado: Objeto ``ResultadoEjecucion`` a persistir.
            limite: Número máximo de registros a conservar. ``0`` = sin límite.
        """
        ruta = self._ruta_para(resultado.id)
        texto = json.dumps(resultado.to_dict(), ensure_ascii=False, indent=2)
        ruta.write_text(texto, encoding="utf-8")
        self._rotar(limite)

    def listar(self) -> list[dict]:
        """
        Retorna un resumen de todos los registros, del más reciente al más antiguo.

        Cada elemento del listado contiene solo los campos de cabecera
        (id, perfil_id, estado, timestamp_inicio, timestamp_fin) para
        minimizar I/O al presentar la vista de historial.

        Los archivos corruptos o inaccesibles se omiten silenciosamente.
        """
        resultado: list[dict] = []
        for archivo in reversed(self._listar_archivos()):
            try:
                datos = json.loads(archivo.read_text(encoding="utf-8"))
                resultado.append(
                    {
                        "id": datos.get("id"),
                        "perfil_id": datos.get("perfil_id"),
                        "estado": datos.get("estado"),
                        "timestamp_inicio": datos.get("timestamp_inicio"),
                        "timestamp_fin": datos.get("timestamp_fin"),
                    }
                )
            except (json.JSONDecodeError, OSError):
                pass
        return resultado

    def obtener(self, resultado_id: str) -> ResultadoEjecucion | None:
        """
        Retorna el ``ResultadoEjecucion`` completo, o ``None`` si no existe o
        el archivo está corrupto.
        """
        ruta = self._ruta_para(resultado_id)
        if not ruta.exists():
            return None
        try:
            datos = json.loads(ruta.read_text(encoding="utf-8"))
            return ResultadoEjecucion.from_dict(datos)
        except (json.JSONDecodeError, KeyError, ValueError):
            return None

    def eliminar(self, resultado_id: str) -> bool:
        """
        Elimina el archivo del registro.

        Returns:
            ``True`` si el archivo existía y fue eliminado, ``False`` si no existía.
        """
        ruta = self._ruta_para(resultado_id)
        if ruta.exists():
            ruta.unlink()
            return True
        return False

    def contar(self) -> int:
        """Retorna el número total de registros almacenados."""
        return len(list(self._dir.glob(f"{FILE_PREFIX}*.json")))
