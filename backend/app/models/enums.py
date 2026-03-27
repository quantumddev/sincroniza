"""
Enumeraciones del dominio de Sincroniza.

Ref: §6.1, §10, §15 del plan de implementación.
"""

from enum import Enum


class EstadoNodo(str, Enum):
    """Estado de un elemento en el árbol de diferencias."""

    NUEVO = "NUEVO"
    MODIFICADO = "MODIFICADO"
    ELIMINADO = "ELIMINADO"
    IDENTICO = "IDENTICO"
    EXCLUIDO = "EXCLUIDO"
    ERROR = "ERROR"
    OMITIDO = "OMITIDO"
    CONFLICTO_NUBE = "CONFLICTO_NUBE"


class MetodoComparacion(str, Enum):
    """Algoritmo usado para comparar archivos."""

    TAMAÑO_FECHA = "TAMAÑO_FECHA"
    HASH = "HASH"


class TipoRegla(str, Enum):
    """Tipo de elemento al que aplica una regla glob."""

    ARCHIVO = "ARCHIVO"
    CARPETA = "CARPETA"
    AMBOS = "AMBOS"


class OrigenRegla(str, Enum):
    """Origen de una regla: predefinida por el sistema o creada por el usuario."""

    SISTEMA = "SISTEMA"
    USUARIO = "USUARIO"


class NivelLog(str, Enum):
    """Nivel de severidad de un evento de log."""

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class EstadoEjecucion(str, Enum):
    """Estado final de una ejecución de sincronización."""

    COMPLETADO = "COMPLETADO"
    COMPLETADO_CON_ERRORES = "COMPLETADO_CON_ERRORES"
    CANCELADO = "CANCELADO"
    FALLIDO = "FALLIDO"


class TipoOperacion(str, Enum):
    """Tipo de operación que el sincronizador ejecutará sobre el destino."""

    COPIAR = "COPIAR"
    REEMPLAZAR = "REEMPLAZAR"
    ELIMINAR_ARCHIVO = "ELIMINAR_ARCHIVO"
    ELIMINAR_CARPETA = "ELIMINAR_CARPETA"
    CREAR_CARPETA = "CREAR_CARPETA"


class TipoElemento(str, Enum):
    """Tipo de elemento del filesystem."""

    ARCHIVO = "ARCHIVO"
    CARPETA = "CARPETA"
    SYMLINK = "SYMLINK"
    OTRO = "OTRO"


class FaseOperacion(str, Enum):
    """Fase de la operación en la que se produce un error."""

    ANALISIS = "analisis"
    EJECUCION = "ejecucion"
