"""
Tests de serialización/deserialización de ResultadoEjecucion.
"""

import pytest

from app.models.enums import (
    EstadoEjecucion,
    FaseOperacion,
    MetodoComparacion,
    TipoOperacion,
)
from app.models.error import ErrorSincronizacion
from app.models.plan import OperacionPlanificada, ResumenPlan
from app.models.resultado import ResultadoEjecucion


@pytest.fixture
def resumen_vacio() -> ResumenPlan:
    return ResumenPlan(
        nuevos=0, modificados=0, eliminados=0, identicos=5,
        excluidos=0, errores=0, conflictos_nube=0, omitidos=0,
        tamaño_copiar=0, tamaño_reemplazar=0, tamaño_eliminar=0,
        total_elementos=5,
    )


@pytest.fixture
def resultado_completado(resumen_vacio, timestamp_iso) -> ResultadoEjecucion:
    return ResultadoEjecucion(
        id="dddddddd-0000-0000-0000-000000000001",
        plan_id="cccccccc-0000-0000-0000-000000000001",
        perfil_id="bbbbbbbb-0000-0000-0000-000000000001",
        origen="C:/origen",
        destino="D:/destino",
        metodo_comparacion=MetodoComparacion.TAMAÑO_FECHA,
        reglas_activas=[],
        estado=EstadoEjecucion.COMPLETADO,
        modo_prueba=False,
        resumen=resumen_vacio,
        operaciones_completadas=[],
        operaciones_fallidas=[],
        errores=[],
        reintentos=[],
        duracion_analisis=1.23,
        duracion_ejecucion=0.45,
        timestamp_inicio=timestamp_iso,
        timestamp_fin=timestamp_iso,
        version_esquema=1,
    )


@pytest.fixture
def resultado_con_errores(resumen_vacio, timestamp_iso) -> ResultadoEjecucion:
    op = OperacionPlanificada(
        tipo=TipoOperacion.COPIAR,
        ruta_origen="C:/origen/a.txt",
        ruta_destino="D:/destino/a.txt",
        ruta_relativa="a.txt",
        tamaño=256,
    )
    err = ErrorSincronizacion(
        codigo="PERMISO_DENEGADO",
        mensaje="Acceso denegado",
        ruta="D:/destino/a.txt",
        fase=FaseOperacion.EJECUCION,
        recuperable=True,
        timestamp=timestamp_iso,
    )
    return ResultadoEjecucion(
        id="dddddddd-0000-0000-0000-000000000002",
        plan_id="cccccccc-0000-0000-0000-000000000001",
        perfil_id="bbbbbbbb-0000-0000-0000-000000000001",
        origen="C:/origen",
        destino="D:/destino",
        metodo_comparacion=MetodoComparacion.HASH,
        reglas_activas=["aaaaaaaa-0000-0000-0000-000000000001"],
        estado=EstadoEjecucion.COMPLETADO_CON_ERRORES,
        modo_prueba=False,
        resumen=resumen_vacio,
        operaciones_completadas=[],
        operaciones_fallidas=[op],
        errores=[err],
        reintentos=[{"ruta": "a.txt", "intento": 1}],
        duracion_analisis=2.0,
        duracion_ejecucion=1.5,
        timestamp_inicio=timestamp_iso,
        timestamp_fin=timestamp_iso,
        version_esquema=1,
    )


def test_resultado_completado_to_dict(resultado_completado):
    d = resultado_completado.to_dict()
    assert d["estado"] == "COMPLETADO"
    assert d["modo_prueba"] is False
    assert d["version_esquema"] == 1
    assert d["operaciones_fallidas"] == []


def test_resultado_completado_round_trip(resultado_completado):
    d = resultado_completado.to_dict()
    reconstruido = ResultadoEjecucion.from_dict(d)
    assert reconstruido.id == resultado_completado.id
    assert reconstruido.estado == EstadoEjecucion.COMPLETADO
    assert reconstruido.duracion_analisis == pytest.approx(1.23)


def test_resultado_con_errores_round_trip(resultado_con_errores):
    d = resultado_con_errores.to_dict()
    reconstruido = ResultadoEjecucion.from_dict(d)
    assert reconstruido.estado == EstadoEjecucion.COMPLETADO_CON_ERRORES
    assert len(reconstruido.operaciones_fallidas) == 1
    assert len(reconstruido.errores) == 1
    assert reconstruido.errores[0].codigo == "PERMISO_DENEGADO"
    assert len(reconstruido.reintentos) == 1


def test_resultado_modo_prueba(resumen_vacio, timestamp_iso):
    r = ResultadoEjecucion(
        id="x", plan_id="y", perfil_id="z",
        origen="C:/a", destino="D:/b",
        metodo_comparacion=MetodoComparacion.HASH,
        reglas_activas=[],
        estado=EstadoEjecucion.COMPLETADO,
        modo_prueba=True,
        resumen=resumen_vacio,
        operaciones_completadas=[], operaciones_fallidas=[],
        errores=[], reintentos=[],
        duracion_analisis=0.1, duracion_ejecucion=0.0,
        timestamp_inicio=timestamp_iso, timestamp_fin=timestamp_iso,
        version_esquema=1,
    )
    d = r.to_dict()
    assert d["modo_prueba"] is True
    assert ResultadoEjecucion.from_dict(d).modo_prueba is True
