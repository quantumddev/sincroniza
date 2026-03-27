"""
Utilidades de normalización de rutas para Windows.

Todas las funciones son puras (sin I/O) salvo `ruta_a_relativa`, que puede
lanzar `ValueError` si las rutas están en unidades distintas.

Ref: §7
"""

import os
from pathlib import PurePosixPath, PureWindowsPath


# ── Prefijos de rutas largas ─────────────────────────────────────────────────

_PREFIJO_LARGO = "\\\\?\\"
_PREFIJO_LARGO_UNC = "\\\\?\\UNC\\"


# ── API pública ──────────────────────────────────────────────────────────────

def normalizar_ruta(ruta: str) -> str:
    """
    Normaliza una ruta aplicando ``os.path.normpath``.

    - Elimina componentes redundantes (``..``, ``.``, dobles separadores).
    - Preserva mayúsculas/minúsculas del sistema de archivos.
    - No realiza I/O.

    Para comparaciones case-insensitive usar ``rutas_iguales()`` en
    ``validaciones.py``.
    """
    return os.path.normpath(ruta)


def normalizar_separadores(ruta: str) -> str:
    """
    Convierte todos los separadores de ruta a ``/`` (convención interna).

    Útil para construir rutas relativas que se almacenan en los modelos,
    independientemente del separador del sistema operativo.
    """
    return ruta.replace("\\", "/")


def quitar_prefijo_largo(ruta: str) -> str:
    """
    Elimina el prefijo ``\\\\?\\`` o ``\\\\?\\UNC\\`` de una ruta extendida.

    Si la ruta no tiene prefijo, se devuelve sin cambios.
    """
    if ruta.startswith(_PREFIJO_LARGO_UNC):
        return "\\\\" + ruta[len(_PREFIJO_LARGO_UNC):]
    if ruta.startswith(_PREFIJO_LARGO):
        return ruta[len(_PREFIJO_LARGO):]
    return ruta


def a_ruta_larga(ruta_absoluta: str) -> str:
    """
    Convierte una ruta absoluta al formato extendido ``\\\\?\\`` de Windows,
    que permite superar el límite de 260 caracteres (MAX_PATH).

    - Rutas locales: ``C:\\...`` → ``\\\\?\\C:\\...``
    - Rutas UNC:     ``\\\\server\\share\\...`` → ``\\\\?\\UNC\\server\\share\\...``

    La ruta de entrada ya debe ser absoluta; no se invoca ``os.path.abspath``
    para mantener la función pura (independiente del directorio de trabajo).
    """
    # Normalizar separadores antes de añadir prefijo
    ruta_norm = os.path.normpath(ruta_absoluta)

    # Evitar doble prefijo
    if ruta_norm.startswith(_PREFIJO_LARGO):
        return ruta_norm

    if ruta_norm.startswith("\\\\"):
        # Ruta UNC: \\server\share → \\?\UNC\server\share
        return _PREFIJO_LARGO_UNC + ruta_norm[2:]

    return _PREFIJO_LARGO + ruta_norm


def ruta_a_relativa(ruta_absoluta: str, raiz: str) -> str:
    """
    Calcula la ruta relativa de ``ruta_absoluta`` respecto a ``raiz``.

    Devuelve la ruta con separadores ``/`` (convención interna).

    Raises:
        ValueError: Si ``ruta_absoluta`` y ``raiz`` están en unidades distintas
                    (p. ej. ``C:\\`` vs ``D:\\``).
    """
    try:
        relativa = os.path.relpath(ruta_absoluta, raiz)
    except ValueError as exc:
        raise ValueError(
            f"No se puede calcular ruta relativa de '{ruta_absoluta}' "
            f"respecto a '{raiz}': {exc}"
        ) from exc
    return normalizar_separadores(relativa)
