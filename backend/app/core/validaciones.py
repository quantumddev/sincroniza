"""
Funciones puras de validación de rutas.

Estas funciones no producen efectos secundarios salvo ``validar_ruta_existe``,
que consulta el sistema de archivos.

Ref: §11
"""

import os
from pathlib import Path


def rutas_iguales(a: str, b: str) -> bool:
    """
    Compara dos rutas de forma case-insensitive (semantica Windows).

    Aplica ``os.path.normcase`` y ``os.path.normpath`` a ambas antes de
    comparar, por lo que diferencias en separadores o redundancias no afectan
    al resultado.

    No realiza I/O.
    """
    return os.path.normcase(os.path.normpath(a)) == os.path.normcase(os.path.normpath(b))


def ruta_anidada(posible_hijo: str, posible_padre: str) -> bool:
    """
    Retorna ``True`` si ``posible_hijo`` es un descendiente directo o indirecto
    de ``posible_padre``.

    Retorna ``False`` si ambas rutas son iguales (una ruta no es hija de sí misma).

    Las rutas deben ser absolutas para obtener un resultado fiable.
    No realiza I/O.

    Ejemplo::

        ruta_anidada("C:/a/b/c", "C:/a")   # True
        ruta_anidada("C:/a",     "C:/a")   # False
        ruta_anidada("C:/abc",   "C:/a")   # False  (evita falsos positivos)
    """
    hijo_norm = os.path.normcase(os.path.normpath(posible_hijo))
    padre_norm = os.path.normcase(os.path.normpath(posible_padre))

    if hijo_norm == padre_norm:
        return False

    # Se añade os.sep al padre para evitar que "/foo/bar" sea considerado
    # hijo de "/foo/ba" (ambos empezarían igual sin el separador).
    return hijo_norm.startswith(padre_norm + os.sep)


def validar_ruta_existe(ruta: str) -> bool:
    """
    Retorna ``True`` si la ruta existe en el sistema de archivos.

    Funciona tanto con archivos como con directorios.
    Una cadena vacía siempre devuelve ``False``.
    """
    if not ruta:
        return False
    return Path(ruta).exists()


def validar_restricciones_opcionales(ruta: str, permitidos: list[str]) -> bool:
    """
    Valida que ``ruta`` esté dentro de alguna de las rutas de la lista blanca.

    - Si ``permitidos`` está vacío, cualquier ruta es válida (sin restricciones).
    - Si no está vacío, ``ruta`` debe ser igual a una ruta permitida o estar
      directamente anidada dentro de ella.

    Las comparaciones son case-insensitive.
    No realiza I/O.
    """
    if not permitidos:
        return True

    ruta_norm = os.path.normcase(os.path.normpath(ruta))
    for permitida in permitidos:
        permitida_norm = os.path.normcase(os.path.normpath(permitida))
        if ruta_norm == permitida_norm:
            return True
        if ruta_norm.startswith(permitida_norm + os.sep):
            return True

    return False
