"""
Tests de serialización/deserialización de ConfiguracionApp y PendingSync.
"""

import pytest

from app.models.configuracion import ConfiguracionApp, PendingSync
from app.models.enums import MetodoComparacion, OrigenRegla, TipoRegla
from app.models.perfil import Perfil
from app.models.regla import Regla


@pytest.fixture
def regla_node_modules() -> Regla:
    return Regla(
        id="aaaaaaaa-0000-0000-0000-000000000001",
        patron="node_modules/**",
        tipo=TipoRegla.CARPETA,
        activa=True,
        origen=OrigenRegla.SISTEMA,
    )


@pytest.fixture
def perfil_simple(timestamp_iso) -> Perfil:
    return Perfil(
        id="bbbbbbbb-0000-0000-0000-000000000001",
        nombre="Documentos",
        origen="C:/docs",
        destino="D:/docs",
        metodo_comparacion=MetodoComparacion.TAMAÑO_FECHA,
        reglas_exclusion_ids=["aaaaaaaa-0000-0000-0000-000000000001"],
        reglas_propias=[],
        umbral_eliminaciones=10,
        timeout_por_archivo=30,
        creado=timestamp_iso,
        ultima_ejecucion=None,
    )


@pytest.fixture
def config_app(perfil_simple, regla_node_modules) -> ConfiguracionApp:
    return ConfiguracionApp(
        version_esquema=1,
        tema="claro",
        metodo_comparacion_defecto=MetodoComparacion.TAMAÑO_FECHA,
        ultimas_rutas={"origen": "C:/docs", "destino": None},
        perfiles=[perfil_simple],
        reglas_exclusion=[regla_node_modules],
        restricciones_ruta={"origen_permitido": [], "destino_permitido": []},
        umbral_eliminaciones=10,
        timeout_por_archivo=30,
        limite_historial=50,
    )


@pytest.fixture
def pending_sync(timestamp_iso) -> PendingSync:
    return PendingSync(
        plan_id="cccccccc-0000-0000-0000-000000000001",
        perfil_id="bbbbbbbb-0000-0000-0000-000000000001",
        timestamp_inicio=timestamp_iso,
        operaciones_completadas=["docs/a.txt", "docs/b.txt"],
        operaciones_pendientes=["docs/c.txt"],
    )


# ── ConfiguracionApp ─────────────────────────────────────────────────────────

def test_config_to_dict_campos_raiz(config_app):
    d = config_app.to_dict()
    assert d["version_esquema"] == 1
    assert d["tema"] == "claro"
    assert d["metodo_comparacion_defecto"] == "TAMAÑO_FECHA"
    assert d["limite_historial"] == 50
    assert isinstance(d["perfiles"], list)
    assert isinstance(d["reglas_exclusion"], list)


def test_config_round_trip(config_app):
    d = config_app.to_dict()
    reconstruido = ConfiguracionApp.from_dict(d)
    assert reconstruido.version_esquema == 1
    assert reconstruido.tema == "claro"
    assert reconstruido.metodo_comparacion_defecto == MetodoComparacion.TAMAÑO_FECHA
    assert len(reconstruido.perfiles) == 1
    assert reconstruido.perfiles[0].nombre == "Documentos"
    assert len(reconstruido.reglas_exclusion) == 1
    assert reconstruido.reglas_exclusion[0].patron == "node_modules/**"


def test_config_ultimas_rutas_none(config_app):
    d = config_app.to_dict()
    assert d["ultimas_rutas"]["destino"] is None
    reconstruido = ConfiguracionApp.from_dict(d)
    assert reconstruido.ultimas_rutas["destino"] is None


def test_config_restricciones_ruta(config_app):
    d = config_app.to_dict()
    assert d["restricciones_ruta"]["origen_permitido"] == []
    reconstruido = ConfiguracionApp.from_dict(d)
    assert reconstruido.restricciones_ruta["origen_permitido"] == []


# ── PendingSync ───────────────────────────────────────────────────────────────

def test_pending_sync_to_dict(pending_sync):
    d = pending_sync.to_dict()
    assert d["plan_id"] == pending_sync.plan_id
    assert len(d["operaciones_completadas"]) == 2
    assert len(d["operaciones_pendientes"]) == 1


def test_pending_sync_round_trip(pending_sync):
    reconstruido = PendingSync.from_dict(pending_sync.to_dict())
    assert reconstruido.plan_id == pending_sync.plan_id
    assert reconstruido.operaciones_completadas == ["docs/a.txt", "docs/b.txt"]
    assert reconstruido.operaciones_pendientes == ["docs/c.txt"]


def test_pending_sync_listas_son_copia(pending_sync):
    """to_dict debe devolver copias de las listas, no referencias."""
    d = pending_sync.to_dict()
    d["operaciones_pendientes"].append("extra.txt")
    assert len(pending_sync.operaciones_pendientes) == 1
