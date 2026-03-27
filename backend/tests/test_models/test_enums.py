"""
Tests de serialización/deserialización de los Enums.
"""

import pytest

from app.models.enums import (
    EstadoEjecucion,
    EstadoNodo,
    FaseOperacion,
    MetodoComparacion,
    NivelLog,
    OrigenRegla,
    TipoElemento,
    TipoOperacion,
    TipoRegla,
)


@pytest.mark.parametrize(
    "enum_cls, value",
    [
        (EstadoNodo, "NUEVO"),
        (EstadoNodo, "MODIFICADO"),
        (EstadoNodo, "ELIMINADO"),
        (EstadoNodo, "IDENTICO"),
        (EstadoNodo, "EXCLUIDO"),
        (EstadoNodo, "ERROR"),
        (EstadoNodo, "OMITIDO"),
        (EstadoNodo, "CONFLICTO_NUBE"),
        (MetodoComparacion, "TAMAÑO_FECHA"),
        (MetodoComparacion, "HASH"),
        (TipoRegla, "ARCHIVO"),
        (TipoRegla, "CARPETA"),
        (TipoRegla, "AMBOS"),
        (OrigenRegla, "SISTEMA"),
        (OrigenRegla, "USUARIO"),
        (NivelLog, "INFO"),
        (NivelLog, "WARNING"),
        (NivelLog, "ERROR"),
        (EstadoEjecucion, "COMPLETADO"),
        (EstadoEjecucion, "COMPLETADO_CON_ERRORES"),
        (EstadoEjecucion, "CANCELADO"),
        (EstadoEjecucion, "FALLIDO"),
        (TipoOperacion, "COPIAR"),
        (TipoOperacion, "REEMPLAZAR"),
        (TipoOperacion, "ELIMINAR_ARCHIVO"),
        (TipoOperacion, "ELIMINAR_CARPETA"),
        (TipoOperacion, "CREAR_CARPETA"),
        (TipoElemento, "ARCHIVO"),
        (TipoElemento, "CARPETA"),
        (TipoElemento, "SYMLINK"),
        (TipoElemento, "OTRO"),
        (FaseOperacion, "analisis"),
        (FaseOperacion, "ejecucion"),
    ],
)
def test_enum_round_trip(enum_cls, value):
    """Cada valor de enum debe poder construirse desde su string y devolver el mismo string."""
    instance = enum_cls(value)
    assert instance.value == value


def test_enums_son_str():
    """Todos los enums heredan de str, por lo que son directamente serializables a JSON."""
    assert isinstance(EstadoNodo.NUEVO, str)
    assert isinstance(MetodoComparacion.HASH, str)
    assert isinstance(FaseOperacion.ANALISIS, str)
