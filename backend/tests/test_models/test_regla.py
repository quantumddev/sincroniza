"""
Tests de serialización/deserialización del modelo Regla.
"""

import pytest

from app.models.enums import OrigenRegla, TipoRegla
from app.models.regla import Regla


@pytest.fixture
def regla_sistema() -> Regla:
    return Regla(
        id="aaaaaaaa-0000-0000-0000-000000000001",
        patron="node_modules/**",
        tipo=TipoRegla.CARPETA,
        activa=True,
        origen=OrigenRegla.SISTEMA,
    )


@pytest.fixture
def regla_usuario() -> Regla:
    return Regla(
        id="aaaaaaaa-0000-0000-0000-000000000002",
        patron="*.tmp",
        tipo=TipoRegla.ARCHIVO,
        activa=False,
        origen=OrigenRegla.USUARIO,
    )


def test_to_dict_contiene_todos_los_campos(regla_sistema):
    d = regla_sistema.to_dict()
    assert d["id"] == regla_sistema.id
    assert d["patron"] == "node_modules/**"
    assert d["tipo"] == "CARPETA"
    assert d["activa"] is True
    assert d["origen"] == "SISTEMA"


def test_from_dict_reconstruye_instancia(regla_sistema):
    d = regla_sistema.to_dict()
    reconstruida = Regla.from_dict(d)
    assert reconstruida == regla_sistema


def test_round_trip_regla_usuario(regla_usuario):
    assert Regla.from_dict(regla_usuario.to_dict()) == regla_usuario


def test_regla_es_frozen():
    """Regla debe ser inmutable."""
    r = Regla(
        id="x",
        patron="*.log",
        tipo=TipoRegla.AMBOS,
        activa=True,
        origen=OrigenRegla.SISTEMA,
    )
    with pytest.raises(Exception):
        r.activa = False  # type: ignore[misc]
