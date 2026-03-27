"""
Evaluación de patrones glob contra rutas relativas del filesystem.

Semántica de los patrones
--------------------------
Se utilizan patrones estilo gitignore con las siguientes reglas:

- ``*``   — coincide con cualquier secuencia de caracteres dentro de un
            componente de ruta (no cruza separadores en pathlib, pero sí en
            posición estándar de nombres).
- ``**``  — coincide con cero o más componentes de ruta (Python 3.12+).
- ``?``   — coincide con exactamente un carácter.
- Los patrones se comparan con ``PurePosixPath.match()`` que aplica la
  coincidencia **desde la derecha**, por lo que un patrón sin ``/`` inicial
  es efectivo **en cualquier nivel** del árbol.
- Un prefijo ``/`` ancla el patrón a la raíz del árbol de diferencias.

Ejemplos::

    evaluar_regla("*.tmp",          "docs/report.tmp",       False) → True
    evaluar_regla("node_modules/**","node_modules/pkg/a.js", True)  → True
    evaluar_regla("node_modules/**","node_modules",          True)  → True
    evaluar_regla(".git/**",        "src/.git/config",       False) → True
    evaluar_regla("*.py",           "lib/util.pyx",          False) → False

Ref: §10
"""

import fnmatch

from app.models.enums import TipoRegla
from app.models.regla import Regla


def evaluar_regla(patron: str, ruta_relativa: str, es_carpeta: bool) -> bool:
    """
    Evalúa si un patrón glob coincide con una ruta relativa.

    Args:
        patron: Patrón glob (p. ej. ``"*.tmp"``, ``"node_modules/**"``).
        ruta_relativa: Ruta relativa al directorio raíz con separadores ``/``.
        es_carpeta: ``True`` si el elemento es un directorio.

    Returns:
        ``True`` si el patrón coincide, ``False`` en caso contrario.

    Notes:
        El algoritmo prueba el patrón contra todos los sufijos de la ruta,
        lo que permite que ``"node_modules/**"`` coincida tanto con
        ``"node_modules/foo.js"`` (raíz) como con ``"src/node_modules/foo.js"``
        (cualquier nivel).

        Reglas adicionales de expansión de patrón:

        - Si el patrón empieza con ``**/``, también se prueba sin ese prefijo
          para cubrir el caso de cero componentes (``"**/.env"`` ↔ ``".env"``).
        - Si el patrón termina con ``/**``, también se prueba sin ese sufijo
          para que el directorio raíz del patrón quede excluido
          (``"node_modules/**"`` ↔ ``"node_modules"``).
    """
    if not ruta_relativa or not patron:
        return False

    ruta_norm = ruta_relativa.replace("\\", "/").strip("/")
    patron_norm = patron.replace("\\", "/").rstrip("/")

    if not ruta_norm or not patron_norm:
        return False

    componentes = ruta_norm.split("/")

    # Todos los sufijos de la ruta (permite match en cualquier nivel).
    sufijos = ["/".join(componentes[i:]) for i in range(len(componentes))]

    # Variantes del patrón a verificar.
    patrones: list[str] = [patron_norm]

    # "**/.env" también debe coincidir con ".env" (** = 0 componentes).
    if patron_norm.startswith("**/"):
        patrones.append(patron_norm[3:])

    # "node_modules/**" también debe coincidir con "node_modules" (el dir mismo).
    if patron_norm.endswith("/**"):
        patrones.append(patron_norm[:-3])

    for p in patrones:
        for sufijo in sufijos:
            if fnmatch.fnmatch(sufijo, p):
                return True

    return False


def evaluar_reglas(
    reglas: list[Regla],
    ruta_relativa: str,
    es_carpeta: bool,
) -> Regla | None:
    """
    Evalúa la lista de reglas activas contra una ruta relativa.

    Itera las reglas en orden y retorna la **primera** regla activa que
    coincide, respetando el campo ``tipo``:

    - ``TipoRegla.ARCHIVO``  — solo aplica a archivos (``es_carpeta=False``).
    - ``TipoRegla.CARPETA``  — solo aplica a directorios (``es_carpeta=True``).
    - ``TipoRegla.AMBOS``    — aplica a ambos.

    Las reglas inactivas (``activa=False``) se saltan siempre.

    Args:
        reglas: Lista ordenada de reglas a evaluar.
        ruta_relativa: Ruta relativa del elemento.
        es_carpeta: ``True`` si el elemento es un directorio.

    Returns:
        La primera ``Regla`` coincidente, o ``None`` si ninguna coincide.
    """
    for regla in reglas:
        if not regla.activa:
            continue

        if regla.tipo == TipoRegla.ARCHIVO and es_carpeta:
            continue
        if regla.tipo == TipoRegla.CARPETA and not es_carpeta:
            continue

        if evaluar_regla(regla.patron, ruta_relativa, es_carpeta):
            return regla

    return None
