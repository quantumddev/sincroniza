"""
Tests de serialización/deserialización de OperacionPlanificada,
ResumenPlan y PlanSincronizacion.
"""

import pytest

from app.models.enums import EstadoNodo, MetodoComparacion, TipoElemento, TipoOperacion
from app.models.nodo_arbol import NodoArbol
from app.models.plan import OperacionPlanificada, PlanSincronizacion, ResumenPlan


@pytest.fixture
def operacion_copiar() -> OperacionPlanificada:
    return OperacionPlanificada(
        tipo=TipoOperacion.COPIAR,
        ruta_origen="C:/origen/docs/readme.md",
        ruta_destino="D:/destino/docs/readme.md",
        ruta_relativa="docs/readme.md",
        tamaño=1024,
    )


@pytest.fixture
def operacion_eliminar() -> OperacionPlanificada:
    return OperacionPlanificada(
        tipo=TipoOperacion.ELIMINAR_ARCHIVO,
        ruta_origen=None,
        ruta_destino="D:/destino/viejo.txt",
        ruta_relativa="viejo.txt",
        tamaño=512,
    )


@pytest.fixture
def resumen_plan() -> ResumenPlan:
    return ResumenPlan(
        nuevos=3,
        modificados=1,
        eliminados=0,
        identicos=10,
        excluidos=2,
        errores=0,
        conflictos_nube=0,
        omitidos=0,
        tamaño_copiar=3072,
        tamaño_reemplazar=1024,
        tamaño_eliminar=0,
        total_elementos=16,
    )


@pytest.fixture
def plan_sincronizacion(resumen_plan, timestamp_iso) -> PlanSincronizacion:
    arbol = NodoArbol(
        nombre="origen",
        ruta_relativa="",
        tipo=TipoElemento.CARPETA,
        estado=EstadoNodo.NUEVO,
        tamaño=0,
        tamaño_destino=None,
        motivo=None,
        hijos=[],
    )
    return PlanSincronizacion(
        id="cccccccc-0000-0000-0000-000000000001",
        perfil_id="bbbbbbbb-0000-0000-0000-000000000001",
        origen="C:/origen",
        destino="D:/destino",
        metodo_comparacion=MetodoComparacion.TAMAÑO_FECHA,
        reglas_activas=["aaaaaaaa-0000-0000-0000-000000000001"],
        arbol=arbol,
        operaciones=[],
        resumen=resumen_plan,
        fingerprint="abcdef1234567890",
        mtime_origen=1743076800.0,
        mtime_destino=1743076700.0,
        timestamp=timestamp_iso,
    )


# ── OperacionPlanificada ─────────────────────────────────────────────────────

def test_operacion_copiar_to_dict(operacion_copiar):
    d = operacion_copiar.to_dict()
    assert d["tipo"] == "COPIAR"
    assert d["ruta_origen"] == "C:/origen/docs/readme.md"
    assert d["tamaño"] == 1024


def test_operacion_round_trip(operacion_copiar):
    assert OperacionPlanificada.from_dict(operacion_copiar.to_dict()) == operacion_copiar


def test_operacion_eliminar_ruta_origen_none(operacion_eliminar):
    d = operacion_eliminar.to_dict()
    assert d["ruta_origen"] is None
    reconstruida = OperacionPlanificada.from_dict(d)
    assert reconstruida.ruta_origen is None


def test_operacion_es_frozen(operacion_copiar):
    with pytest.raises(Exception):
        operacion_copiar.tamaño = 0  # type: ignore[misc]


# ── ResumenPlan ──────────────────────────────────────────────────────────────

def test_resumen_round_trip(resumen_plan):
    reconstruido = ResumenPlan.from_dict(resumen_plan.to_dict())
    assert reconstruido == resumen_plan


def test_resumen_es_frozen(resumen_plan):
    with pytest.raises(Exception):
        resumen_plan.nuevos = 99  # type: ignore[misc]


# ── PlanSincronizacion ───────────────────────────────────────────────────────

def test_plan_to_dict_campos_raiz(plan_sincronizacion):
    d = plan_sincronizacion.to_dict()
    assert d["id"] == plan_sincronizacion.id
    assert d["metodo_comparacion"] == "TAMAÑO_FECHA"
    assert d["fingerprint"] == "abcdef1234567890"
    assert isinstance(d["arbol"], dict)
    assert isinstance(d["resumen"], dict)


def test_plan_round_trip(plan_sincronizacion):
    d = plan_sincronizacion.to_dict()
    reconstruido = PlanSincronizacion.from_dict(d)
    assert reconstruido.id == plan_sincronizacion.id
    assert reconstruido.metodo_comparacion == MetodoComparacion.TAMAÑO_FECHA
    assert reconstruido.resumen.nuevos == 3
    assert reconstruido.arbol.tipo == TipoElemento.CARPETA
