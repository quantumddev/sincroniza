"""
Tests de serialización/deserialización del modelo Perfil.
"""

import pytest

from app.models.enums import MetodoComparacion, OrigenRegla, TipoRegla
from app.models.perfil import Perfil
from app.models.regla import Regla


@pytest.fixture
def perfil_minimo(timestamp_iso) -> Perfil:
    return Perfil(
        id="bbbbbbbb-0000-0000-0000-000000000001",
        nombre="Backup Documentos",
        origen="C:/Users/jaime/Documents",
        destino="D:/Backup/Documents",
        metodo_comparacion=MetodoComparacion.TAMAÑO_FECHA,
        reglas_exclusion_ids=["aaaaaaaa-0000-0000-0000-000000000001"],
        reglas_propias=[],
        umbral_eliminaciones=10,
        timeout_por_archivo=30,
        creado=timestamp_iso,
        ultima_ejecucion=None,
    )


@pytest.fixture
def perfil_con_regla(timestamp_iso) -> Perfil:
    regla = Regla(
        id="aaaaaaaa-0000-0000-0000-000000000003",
        patron="*.bak",
        tipo=TipoRegla.ARCHIVO,
        activa=True,
        origen=OrigenRegla.USUARIO,
    )
    return Perfil(
        id="bbbbbbbb-0000-0000-0000-000000000002",
        nombre="Sync Proyectos",
        origen="C:/dev",
        destino="E:/dev-backup",
        metodo_comparacion=MetodoComparacion.HASH,
        reglas_exclusion_ids=[],
        reglas_propias=[regla],
        umbral_eliminaciones=5,
        timeout_por_archivo=60,
        creado=timestamp_iso,
        ultima_ejecucion=timestamp_iso,
    )


def test_to_dict_campos_basicos(perfil_minimo):
    d = perfil_minimo.to_dict()
    assert d["id"] == perfil_minimo.id
    assert d["nombre"] == "Backup Documentos"
    assert d["metodo_comparacion"] == "TAMAÑO_FECHA"
    assert d["ultima_ejecucion"] is None
    assert d["reglas_propias"] == []


def test_round_trip_perfil_minimo(perfil_minimo):
    reconstruido = Perfil.from_dict(perfil_minimo.to_dict())
    assert reconstruido.id == perfil_minimo.id
    assert reconstruido.nombre == perfil_minimo.nombre
    assert reconstruido.metodo_comparacion == perfil_minimo.metodo_comparacion
    assert reconstruido.ultima_ejecucion is None


def test_round_trip_perfil_con_regla(perfil_con_regla):
    d = perfil_con_regla.to_dict()
    reconstruido = Perfil.from_dict(d)
    assert len(reconstruido.reglas_propias) == 1
    assert reconstruido.reglas_propias[0].patron == "*.bak"
    assert reconstruido.ultima_ejecucion == perfil_con_regla.ultima_ejecucion


def test_reglas_exclusion_ids_son_copia(perfil_minimo):
    """to_dict debe devolver una copia de la lista de ids, no la referencia."""
    d = perfil_minimo.to_dict()
    d["reglas_exclusion_ids"].append("extra")
    assert len(perfil_minimo.reglas_exclusion_ids) == 1
