"""
PendingSyncStorage — gestión de ``data/pending_sync.json``.

Este archivo temporal señala que hay una sincronización que fue interrumpida
(crash, corte de energía, etc.) antes de completarse. Al iniciar la aplicación,
si el archivo existe, se ofrece al usuario la posibilidad de revisar el estado
e intentar recuperación manual.

Ref: §6.5
"""

from __future__ import annotations

import json
from pathlib import Path

from app.models.configuracion import PendingSync

# Nombre del archivo relativo al directorio ``data/``.
PENDING_FILE = "pending_sync.json"


class PendingSyncStorage:
    """
    Crea, lee y elimina ``data/pending_sync.json``.

    Args:
        data_dir: Ruta al directorio ``data/``.
    """

    def __init__(self, data_dir: Path) -> None:
        self._path = data_dir / PENDING_FILE

    # ── API pública ───────────────────────────────────────────────────────────

    def existe(self) -> bool:
        """Retorna ``True`` si hay una sincronización pendiente en disco."""
        return self._path.exists()

    def guardar(self, pending: PendingSync) -> None:
        """
        Persiste el estado de la sincronización en curso.

        Crea el directorio padre si no existe.
        """
        self._path.parent.mkdir(parents=True, exist_ok=True)
        texto = json.dumps(pending.to_dict(), ensure_ascii=False, indent=2)
        self._path.write_text(texto, encoding="utf-8")

    def leer(self) -> PendingSync | None:
        """
        Retorna el ``PendingSync`` almacenado.

        Returns:
            La instancia si el archivo existe y es válido, ``None`` en caso
            contrario (archivo inexistente o JSON corrupto).
        """
        if not self._path.exists():
            return None
        try:
            datos = json.loads(self._path.read_text(encoding="utf-8"))
            return PendingSync.from_dict(datos)
        except (json.JSONDecodeError, KeyError, ValueError):
            return None

    def eliminar(self) -> bool:
        """
        Elimina el archivo de sincronización pendiente.

        Returns:
            ``True`` si el archivo existía y fue eliminado, ``False`` si no
            existía (idempotente).
        """
        if self._path.exists():
            self._path.unlink()
            return True
        return False

    @property
    def ruta(self) -> Path:
        """Ruta absoluta al archivo ``pending_sync.json``."""
        return self._path
