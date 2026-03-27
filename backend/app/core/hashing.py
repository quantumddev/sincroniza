"""
Cálculo de hash SHA-256 de archivos mediante lectura por bloques.

La lectura por bloques garantiza un uso de memoria acotado incluso para
archivos de varios gigabytes.

Ref: §7
"""

import hashlib

TAMAÑO_BLOQUE_DEFECTO: int = 65_536  # 64 KiB


def calcular_hash_archivo(
    ruta: str,
    tamaño_bloque: int = TAMAÑO_BLOQUE_DEFECTO,
) -> str:
    """
    Calcula el hash SHA-256 hexadecimal del contenido de un archivo.

    Lee el archivo en bloques de ``tamaño_bloque`` bytes para evitar cargar
    el fichero entero en memoria.

    Args:
        ruta: Ruta absoluta o relativa al archivo.
        tamaño_bloque: Número de bytes leídos por iteración. Por defecto 64 KiB.

    Returns:
        String hexadecimal de 64 caracteres con el digest SHA-256.

    Raises:
        FileNotFoundError: Si el archivo no existe.
        PermissionError: Si no hay permisos de lectura.
        OSError: Para cualquier otro error de I/O.
        ValueError: Si ``tamaño_bloque`` no es un entero positivo.
    """
    if tamaño_bloque <= 0:
        raise ValueError(
            f"tamaño_bloque debe ser un entero positivo, se recibió {tamaño_bloque!r}"
        )

    digest = hashlib.sha256()
    with open(ruta, "rb") as f:
        while bloque := f.read(tamaño_bloque):
            digest.update(bloque)

    return digest.hexdigest()
