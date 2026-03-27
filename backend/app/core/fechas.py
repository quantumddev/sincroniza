"""
Utilidades de fechas y timestamps.

Gestiona la obtención del mtime del sistema de archivos y la conversión
a strings ISO 8601 con zona horaria UTC.

Ref: §6.3
"""

import os
from datetime import datetime, timezone


def obtener_mtime(ruta: str) -> float:
    """
    Retorna el timestamp de última modificación (mtime) de una ruta.

    Funciona tanto con archivos como con directorios.

    Args:
        ruta: Ruta al archivo o directorio.

    Returns:
        Timestamp POSIX como ``float`` (segundos desde la época Unix).

    Raises:
        FileNotFoundError: Si la ruta no existe.
        PermissionError: Si no hay acceso a los metadatos.
        OSError: Para cualquier otro error de I/O.
    """
    return os.path.getmtime(ruta)


def timestamp_ahora() -> str:
    """
    Retorna el timestamp actual en formato ISO 8601 con zona horaria UTC.

    Ejemplo de salida: ``"2026-03-27T12:00:00+00:00"``
    """
    return datetime.now(tz=timezone.utc).isoformat()


def timestamp_a_iso(ts: float) -> str:
    """
    Convierte un timestamp POSIX (float) a string ISO 8601 con zona UTC.

    Args:
        ts: Segundos desde la época Unix.

    Returns:
        String ISO 8601, p. ej. ``"2026-03-27T12:00:00+00:00"``.
    """
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def iso_a_timestamp(iso: str) -> float:
    """
    Convierte un string ISO 8601 a timestamp POSIX (float).

    Admite strings con y sin información de zona horaria. Si no tiene zona
    horaria, se asume UTC.

    Args:
        iso: String ISO 8601, p. ej. ``"2026-03-27T12:00:00+00:00"``.

    Returns:
        Segundos desde la época Unix como ``float``.

    Raises:
        ValueError: Si el string no tiene formato ISO 8601 válido.
    """
    dt = datetime.fromisoformat(iso)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.timestamp()
