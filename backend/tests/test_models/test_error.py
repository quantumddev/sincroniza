"""
Tests de serialización/deserialización del modelo ErrorSincronizacion.
"""

import pytest

from app.models.enums import FaseOperacion
from app.models.error import ErrorSincronizacion


@pytest.fixture
def error_recuperable(timestamp_iso) -> ErrorSincronizacion:
    return ErrorSincronizacion(
        codigo="PERMISO_DENEGADO",
        mensaje="No se puede acceder al archivo: acceso denegado",
        ruta="C:/destino/archivo_bloqueado.txt",
        fase=FaseOperacion.EJECUCION,
        recuperable=True,
        timestamp=timestamp_iso,
    )


@pytest.fixture
def error_no_recuperable(timestamp_iso) -> ErrorSincronizacion:
    return ErrorSincronizacion(
        codigo="DISCO_LLENO",
        mensaje="No hay espacio suficiente en el disco destino",
        ruta="D:/backup",
        fase=FaseOperacion.EJECUCION,
        recuperable=False,
        timestamp=timestamp_iso,
    )


def test_to_dict_serializa_fase(error_recuperable):
    d = error_recuperable.to_dict()
    assert d["fase"] == "ejecucion"
    assert d["codigo"] == "PERMISO_DENEGADO"
    assert d["recuperable"] is True


def test_round_trip_recuperable(error_recuperable):
    reconstruido = ErrorSincronizacion.from_dict(error_recuperable.to_dict())
    assert reconstruido == error_recuperable
    assert reconstruido.fase == FaseOperacion.EJECUCION


def test_round_trip_no_recuperable(error_no_recuperable):
    reconstruido = ErrorSincronizacion.from_dict(error_no_recuperable.to_dict())
    assert reconstruido == error_no_recuperable
    assert reconstruido.recuperable is False


def test_error_es_frozen(error_recuperable):
    with pytest.raises(Exception):
        error_recuperable.codigo = "OTRO"  # type: ignore[misc]


def test_error_fase_analisis(timestamp_iso):
    error = ErrorSincronizacion(
        codigo="RUTA_INVALIDA",
        mensaje="La ruta origen no existe",
        ruta="Z:/no_existe",
        fase=FaseOperacion.ANALISIS,
        recuperable=False,
        timestamp=timestamp_iso,
    )
    d = error.to_dict()
    assert d["fase"] == "analisis"
    assert ErrorSincronizacion.from_dict(d).fase == FaseOperacion.ANALISIS
