"""
Tests para HistorialServicio.

Verifica guardar respetando límite, listado paginado, obtención por ID
y eliminación de entradas.
"""

from __future__ import annotations

import uuid

import pytest

from app.models.enums import EstadoEjecucion, MetodoComparacion
from app.models.nodo_arbol import NodoArbol
from app.models.enums import EstadoNodo, TipoElemento
from app.models.plan import ResumenPlan
from app.models.resultado import ResultadoEjecucion
from app.services.historial import HistorialServicio
from app.storage.config_storage import ConfigStorage
from app.storage.historial_storage import HistorialStorage


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture()
def config_storage(tmp_path) -> ConfigStorage:
    return ConfigStorage(tmp_path)


@pytest.fixture()
def historial_storage(tmp_path) -> HistorialStorage:
    return HistorialStorage(tmp_path)


@pytest.fixture()
def servicio(historial_storage, config_storage) -> HistorialServicio:
    return HistorialServicio(historial_storage, config_storage)


# ── Helpers ───────────────────────────────────────────────────────────────────


def _resumen() -> ResumenPlan:
    return ResumenPlan(
        nuevos=0, modificados=0, eliminados=0, identicos=0,
        excluidos=0, errores=0, conflictos_nube=0, omitidos=0,
        tamaño_copiar=0, tamaño_reemplazar=0, tamaño_eliminar=0,
        total_elementos=0,
    )


def _resultado(rid: str | None = None) -> ResultadoEjecucion:
    return ResultadoEjecucion(
        id=rid or str(uuid.uuid4()),
        plan_id="plan-1",
        perfil_id="p1",
        origen="/src",
        destino="/dst",
        metodo_comparacion=MetodoComparacion.TAMAÑO_FECHA,
        reglas_activas=[],
        estado=EstadoEjecucion.COMPLETADO,
        modo_prueba=False,
        resumen=_resumen(),
        operaciones_completadas=[],
        operaciones_fallidas=[],
        errores=[],
        reintentos=[],
        duracion_analisis=0.0,
        duracion_ejecucion=1.0,
        timestamp_inicio="2024-01-01T00:00:00",
        timestamp_fin="2024-01-01T00:00:01",
        version_esquema=1,
    )


# ── TestGuardar ────────────────────────────────────────────────────────────────


class TestGuardar:
    def test_guardar_y_recuperar(self, servicio: HistorialServicio) -> None:
        r = _resultado("r1")
        servicio.guardar(r)
        recuperado = servicio.obtener("r1")
        assert recuperado is not None
        assert recuperado.id == "r1"

    def test_guardar_respeta_limite(
        self, historial_storage, config_storage
    ) -> None:
        # Establecer límite = 2
        config = config_storage.leer()
        config.limite_historial = 2
        config_storage.escribir(config)

        serv = HistorialServicio(historial_storage, config_storage)
        for i in range(5):
            serv.guardar(_resultado(f"r{i}"))

        pagina = serv.listar(pagina=1, limite=100)
        assert pagina["total"] <= 2

    def test_guardar_multiples(self, servicio: HistorialServicio) -> None:
        for i in range(3):
            servicio.guardar(_resultado(f"x{i}"))
        pagina = servicio.listar(pagina=1, limite=100)
        assert pagina["total"] == 3


# ── TestListar ─────────────────────────────────────────────────────────────────


class TestListar:
    def test_listar_vacio(self, servicio: HistorialServicio) -> None:
        pagina = servicio.listar()
        assert pagina["total"] == 0
        assert pagina["items"] == []

    def test_listar_primera_pagina(self, servicio: HistorialServicio) -> None:
        for i in range(5):
            servicio.guardar(_resultado(f"p{i}"))
        pagina = servicio.listar(pagina=1, limite=3)
        assert pagina["total"] == 5
        assert len(pagina["items"]) == 3

    def test_listar_segunda_pagina(self, servicio: HistorialServicio) -> None:
        for i in range(5):
            servicio.guardar(_resultado(f"q{i}"))
        pagina = servicio.listar(pagina=2, limite=3)
        assert len(pagina["items"]) == 2  # 5 - 3 = 2 restantes

    def test_listar_pagina_mayor_al_total(
        self, servicio: HistorialServicio
    ) -> None:
        servicio.guardar(_resultado("u1"))
        pagina = servicio.listar(pagina=99, limite=10)
        assert pagina["items"] == []
        assert pagina["total"] == 1

    def test_listar_retorna_resultado_ejecucion(
        self, servicio: HistorialServicio
    ) -> None:
        servicio.guardar(_resultado("z1"))
        pagina = servicio.listar()
        assert isinstance(pagina["items"][0], dict)
        assert pagina["items"][0]["id"] == "z1"


# ── TestObtener ────────────────────────────────────────────────────────────────


class TestObtener:
    def test_obtener_existente(self, servicio: HistorialServicio) -> None:
        servicio.guardar(_resultado("m1"))
        resultado = servicio.obtener("m1")
        assert resultado is not None
        assert resultado.id == "m1"

    def test_obtener_no_existente(self, servicio: HistorialServicio) -> None:
        assert servicio.obtener("no-existe") is None


# ── TestEliminar ───────────────────────────────────────────────────────────────


class TestEliminar:
    def test_eliminar_existente(self, servicio: HistorialServicio) -> None:
        servicio.guardar(_resultado("d1"))
        assert servicio.eliminar("d1") is True
        assert servicio.obtener("d1") is None

    def test_eliminar_no_existente(self, servicio: HistorialServicio) -> None:
        assert servicio.eliminar("fantasma") is False

    def test_eliminar_persiste(self, servicio: HistorialServicio) -> None:
        servicio.guardar(_resultado("e1"))
        servicio.eliminar("e1")
        assert servicio.listar()["total"] == 0
