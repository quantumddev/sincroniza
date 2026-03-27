"""
Cálculo del fingerprint de un plan de sincronización.

El fingerprint es un hash SHA-256 determinista de los parámetros clave del
análisis: rutas, reglas activas y método de comparación. Permite detectar
si el plan ha quedado desactualizado antes de ejecutarlo.

Ref: §6.3
"""

import hashlib
import json
import os

from app.models.enums import MetodoComparacion


def calcular_fingerprint(
    origen: str,
    destino: str,
    reglas_activas_ids: list[str],
    metodo: MetodoComparacion,
) -> str:
    """
    Calcula un hash SHA-256 determinista de los parámetros del plan.

    La función es:

    - **Determinista**: los mismos argumentos siempre producen el mismo hash.
    - **Sensible al orden de rutas**: ``origen`` y ``destino`` son posicionales.
    - **Independiente del orden de reglas**: ``reglas_activas_ids`` se ordena
      antes de serializar.
    - **Reproducible**: utiliza ``json.dumps`` con ``sort_keys=True`` y
      codificación UTF-8 estricta.

    Args:
        origen: Ruta absoluta del directorio origen (se normaliza internamente).
        destino: Ruta absoluta del directorio destino (se normaliza internamente).
        reglas_activas_ids: Lista de IDs de las reglas activas aplicadas.
        metodo: Método de comparación utilizado.

    Returns:
        String hexadecimal de 64 caracteres con el digest SHA-256.
    """
    datos: dict = {
        "origen": os.path.normcase(os.path.normpath(origen)),
        "destino": os.path.normcase(os.path.normpath(destino)),
        "reglas": sorted(reglas_activas_ids),
        "metodo": metodo.value,
    }
    serializado = json.dumps(datos, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(serializado.encode("utf-8")).hexdigest()
