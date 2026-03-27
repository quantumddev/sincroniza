"""
ExploradorServicio — Exploración recursiva de directorios del filesystem.

Analiza un árbol de directorios y devuelve una lista plana de
``EntradaFilesystem``, incluyendo detección de archivos ocultos,
symlinks y soporte de rutas largas en Windows (prefijo ``\\\\?\\``).

Ref: §11
"""

from __future__ import annotations

import os
import stat
import sys

from app.core.normalizacion import ruta_a_relativa
from app.models.enums import TipoElemento
from app.models.nodo_arbol import EntradaFilesystem


def _es_oculto(entry: os.DirEntry) -> bool:
    """
    Determina si una entrada del filesystem es oculta.

    En Windows se consulta el atributo ``FILE_ATTRIBUTE_HIDDEN``; en otros
    sistemas se comprueba si el nombre comienza con un punto.
    """
    if entry.name.startswith("."):
        return True
    if sys.platform == "win32":
        try:
            atributos = entry.stat(follow_symlinks=False).st_file_attributes
            return bool(atributos & stat.FILE_ATTRIBUTE_HIDDEN)
        except (OSError, AttributeError):
            pass
    return False


class ExploradorServicio:
    """
    Explora recursivamente un directorio y produce una lista de entradas.

    No sigue symlinks para evitar ciclos.
    Los errores de permiso o lectura en entradas individuales se ignoran
    de forma silenciosa para no abortar el análisis completo.
    """

    def explorar(self, raiz: str) -> list[EntradaFilesystem]:
        """
        Recorre ``raiz`` recursivamente y devuelve todas las entradas.

        Args:
            raiz: Ruta absoluta del directorio raíz a explorar.

        Returns:
            Lista de ``EntradaFilesystem`` con rutas relativas al ``raiz``.
        """
        entradas: list[EntradaFilesystem] = []
        self._explorar_dir(raiz, raiz, entradas)
        return entradas

    # ── Privado ───────────────────────────────────────────────────────────────

    def _explorar_dir(
        self,
        raiz: str,
        directorio: str,
        entradas: list[EntradaFilesystem],
    ) -> None:
        try:
            with os.scandir(directorio) as it:
                for entry in it:
                    self._procesar_entry(raiz, entry, entradas)
        except (PermissionError, OSError):
            pass

    def _procesar_entry(
        self,
        raiz: str,
        entry: os.DirEntry,
        entradas: list[EntradaFilesystem],
    ) -> None:
        try:
            es_symlink = entry.is_symlink()
            es_oculto = _es_oculto(entry)

            if es_symlink:
                tipo = TipoElemento.SYMLINK
                st = entry.stat(follow_symlinks=False)
                tamaño = st.st_size
                mtime = st.st_mtime
            elif entry.is_dir(follow_symlinks=False):
                tipo = TipoElemento.CARPETA
                st = entry.stat(follow_symlinks=False)
                tamaño = 0
                mtime = st.st_mtime
            elif entry.is_file(follow_symlinks=False):
                tipo = TipoElemento.ARCHIVO
                st = entry.stat(follow_symlinks=False)
                tamaño = st.st_size
                mtime = st.st_mtime
            else:
                tipo = TipoElemento.OTRO
                st = entry.stat(follow_symlinks=False)
                tamaño = 0
                mtime = st.st_mtime

            ruta_rel = ruta_a_relativa(entry.path, raiz)

            entradas.append(
                EntradaFilesystem(
                    ruta_relativa=ruta_rel,
                    tipo=tipo,
                    tamaño=tamaño,
                    mtime=mtime,
                    es_oculto=es_oculto,
                    es_symlink=es_symlink,
                )
            )

            # Recursión sólo en carpetas reales (no symlinks)
            if tipo == TipoElemento.CARPETA:
                self._explorar_dir(raiz, entry.path, entradas)

        except (PermissionError, OSError):
            pass
