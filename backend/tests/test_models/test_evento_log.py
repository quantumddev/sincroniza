"""
Tests de serialización/deserialización de EventoLog.
"""

import pytest

from app.models.enums import NivelLog
from app.models.evento_log import EventoLog


@pytest.fixture
def evento_info(timestamp_iso) -> EventoLog:
    return EventoLog(
        tipo="analisis.progreso",
        nivel=NivelLog.INFO,
        mensaje="Analizando directorio: docs/",
        datos={"ruta": "docs/", "elementos_procesados": 42},
        timestamp=timestamp_iso,
    )


@pytest.fixture
def evento_error_sin_datos(timestamp_iso) -> EventoLog:
    return EventoLog(
        tipo="sync.error",
        nivel=NivelLog.ERROR,
        mensaje="Error inesperado durante la copia",
        datos=None,
        timestamp=timestamp_iso,
    )


def test_to_dict_con_datos(evento_info):
    d = evento_info.to_dict()
    assert d["tipo"] == "analisis.progreso"
    assert d["nivel"] == "INFO"
    assert d["datos"]["elementos_procesados"] == 42


def test_round_trip_con_datos(evento_info):
    reconstruido = EventoLog.from_dict(evento_info.to_dict())
    assert reconstruido == evento_info
    assert reconstruido.nivel == NivelLog.INFO


def test_round_trip_datos_none(evento_error_sin_datos):
    d = evento_error_sin_datos.to_dict()
    assert d["datos"] is None
    reconstruido = EventoLog.from_dict(d)
    assert reconstruido.datos is None


def test_evento_es_frozen(evento_info):
    with pytest.raises(Exception):
        evento_info.tipo = "otro"  # type: ignore[misc]
