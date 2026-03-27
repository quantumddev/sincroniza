"""
Tests para SincronizadorServicio.

Verifica la ejecución de operaciones, escrituras atómicas, cancelación,
modo prueba y generación del ResultadoEjecucion.
"""

from __future__ import annotations

import os
import threading

import pytest

from app.models.enums import (
    EstadoEjecucion,
    MetodoComparacion,
    TipoOperacion,
)
from app.models.nodo_arbol import NodoArbol
from app.models.enums import EstadoNodo, TipoElemento
from app.models.plan import OperacionPlanificada, PlanSincronizacion, ResumenPlan
from app.services.log import LogServicio
from app.services.sincronizador import SincronizadorServicio
from app.storage.pending_storage import PendingSyncStorage


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture()
def log() -> LogServicio:
    return LogServicio()


@pytest.fixture()
def pending(tmp_path) -> PendingSyncStorage:
    return PendingSyncStorage(tmp_path)


@pytest.fixture()
def sincronizador(pending, log) -> SincronizadorServicio:
    return SincronizadorServicio(pending, log)


def _resumen_vacio() -> ResumenPlan:
    return ResumenPlan(
        nuevos=0, modificados=0, eliminados=0, identicos=0,
        excluidos=0, errores=0, conflictos_nube=0, omitidos=0,
        tamaño_copiar=0, tamaño_reemplazar=0, tamaño_eliminar=0,
        total_elementos=0,
    )


def _nodo_raiz() -> NodoArbol:
    return NodoArbol(
        nombre="", ruta_relativa="",
        tipo=TipoElemento.CARPETA, estado=EstadoNodo.IDENTICO,
        tamaño=0, tamaño_destino=0, motivo=None,
    )


def _plan(
    operaciones: list[OperacionPlanificada],
    origen: str = "/origen",
    destino: str = "/destino",
) -> PlanSincronizacion:
    return PlanSincronizacion(
        id="plan-1",
        perfil_id="p1",
        origen=origen,
        destino=destino,
        metodo_comparacion=MetodoComparacion.TAMAÑO_FECHA,
        reglas_activas=[],
        arbol=_nodo_raiz(),
        operaciones=operaciones,
        resumen=_resumen_vacio(),
        fingerprint="abc" * 21 + "a",
        mtime_origen=0.0,
        mtime_destino=0.0,
        timestamp="2024-01-01T00:00:00",
    )


# ── TestModoPrueba ────────────────────────────────────────────────────────────


class TestModoPrueba:
    def test_modo_prueba_no_crea_archivos(
        self, sincronizador: SincronizadorServicio, tmp_path
    ) -> None:
        origen = tmp_path / "origen"
        destino = tmp_path / "destino"
        origen.mkdir(); destino.mkdir()
        (origen / "f.txt").write_text("x")

        op = OperacionPlanificada(
            tipo=TipoOperacion.COPIAR,
            ruta_origen=str(origen / "f.txt"),
            ruta_destino=str(destino / "f.txt"),
            ruta_relativa="f.txt",
            tamaño=1,
        )
        plan = _plan([op], str(origen), str(destino))
        resultado = sincronizador.ejecutar(plan, threading.Event(), modo_prueba=True)

        assert resultado.estado == EstadoEjecucion.COMPLETADO
        assert not (destino / "f.txt").exists()

    def test_modo_prueba_todas_completadas(
        self, sincronizador: SincronizadorServicio, tmp_path
    ) -> None:
        origen = tmp_path / "origen"
        destino = tmp_path / "destino"
        origen.mkdir(); destino.mkdir()

        ops = [
            OperacionPlanificada(
                tipo=TipoOperacion.COPIAR,
                ruta_origen=str(origen / f"f{i}.txt"),
                ruta_destino=str(destino / f"f{i}.txt"),
                ruta_relativa=f"f{i}.txt",
                tamaño=1,
            )
            for i in range(3)
        ]
        resultado = sincronizador.ejecutar(
            _plan(ops, str(origen), str(destino)), threading.Event(), modo_prueba=True
        )
        assert len(resultado.operaciones_completadas) == 3
        assert resultado.operaciones_fallidas == []


# ── TestEjecucionReal ─────────────────────────────────────────────────────────


class TestEjecucionReal:
    def test_copiar_archivo(
        self, sincronizador: SincronizadorServicio, tmp_path
    ) -> None:
        origen = tmp_path / "origen"
        destino = tmp_path / "destino"
        origen.mkdir(); destino.mkdir()
        (origen / "arch.txt").write_bytes(b"contenido")

        op = OperacionPlanificada(
            tipo=TipoOperacion.COPIAR,
            ruta_origen=str(origen / "arch.txt"),
            ruta_destino=str(destino / "arch.txt"),
            ruta_relativa="arch.txt",
            tamaño=9,
        )
        resultado = sincronizador.ejecutar(_plan([op], str(origen), str(destino)), threading.Event())
        assert resultado.estado == EstadoEjecucion.COMPLETADO
        assert (destino / "arch.txt").read_bytes() == b"contenido"

    def test_crear_carpeta(
        self, sincronizador: SincronizadorServicio, tmp_path
    ) -> None:
        origen = tmp_path / "origen"
        destino = tmp_path / "destino"
        origen.mkdir(); destino.mkdir()

        op = OperacionPlanificada(
            tipo=TipoOperacion.CREAR_CARPETA,
            ruta_origen=None,
            ruta_destino=str(destino / "nueva"),
            ruta_relativa="nueva",
            tamaño=0,
        )
        resultado = sincronizador.ejecutar(_plan([op], str(origen), str(destino)), threading.Event())
        assert resultado.estado == EstadoEjecucion.COMPLETADO
        assert (destino / "nueva").is_dir()

    def test_eliminar_archivo(
        self, sincronizador: SincronizadorServicio, tmp_path
    ) -> None:
        origen = tmp_path / "origen"
        destino = tmp_path / "destino"
        origen.mkdir(); destino.mkdir()
        (destino / "viejo.txt").write_text("x")

        op = OperacionPlanificada(
            tipo=TipoOperacion.ELIMINAR_ARCHIVO,
            ruta_origen=None,
            ruta_destino=str(destino / "viejo.txt"),
            ruta_relativa="viejo.txt",
            tamaño=1,
        )
        resultado = sincronizador.ejecutar(_plan([op], str(origen), str(destino)), threading.Event())
        assert resultado.estado == EstadoEjecucion.COMPLETADO
        assert not (destino / "viejo.txt").exists()

    def test_reemplazar_archivo(
        self, sincronizador: SincronizadorServicio, tmp_path
    ) -> None:
        origen = tmp_path / "origen"
        destino = tmp_path / "destino"
        origen.mkdir(); destino.mkdir()
        (origen / "doc.txt").write_bytes(b"nuevo")
        (destino / "doc.txt").write_bytes(b"viejo")

        op = OperacionPlanificada(
            tipo=TipoOperacion.REEMPLAZAR,
            ruta_origen=str(origen / "doc.txt"),
            ruta_destino=str(destino / "doc.txt"),
            ruta_relativa="doc.txt",
            tamaño=5,
        )
        resultado = sincronizador.ejecutar(_plan([op], str(origen), str(destino)), threading.Event())
        assert resultado.estado == EstadoEjecucion.COMPLETADO
        assert (destino / "doc.txt").read_bytes() == b"nuevo"

    def test_eliminar_carpeta(
        self, sincronizador: SincronizadorServicio, tmp_path
    ) -> None:
        origen = tmp_path / "origen"
        destino = tmp_path / "destino"
        origen.mkdir(); destino.mkdir()
        (destino / "huerfana").mkdir()
        (destino / "huerfana" / "x.txt").write_text("x")

        op = OperacionPlanificada(
            tipo=TipoOperacion.ELIMINAR_CARPETA,
            ruta_origen=None,
            ruta_destino=str(destino / "huerfana"),
            ruta_relativa="huerfana",
            tamaño=0,
        )
        resultado = sincronizador.ejecutar(_plan([op], str(origen), str(destino)), threading.Event())
        assert resultado.estado == EstadoEjecucion.COMPLETADO
        assert not (destino / "huerfana").exists()


# ── TestCancelacion ───────────────────────────────────────────────────────────


class TestCancelacion:
    def test_cancelacion_inmediata(
        self, sincronizador: SincronizadorServicio, tmp_path
    ) -> None:
        origen = tmp_path / "origen"
        destino = tmp_path / "destino"
        origen.mkdir(); destino.mkdir()
        (origen / "f.txt").write_text("x")

        op = OperacionPlanificada(
            tipo=TipoOperacion.COPIAR,
            ruta_origen=str(origen / "f.txt"),
            ruta_destino=str(destino / "f.txt"),
            ruta_relativa="f.txt",
            tamaño=1,
        )
        cancel = threading.Event()
        cancel.set()  # Ya cancelado antes de empezar

        resultado = sincronizador.ejecutar(_plan([op], str(origen), str(destino)), cancel)
        assert resultado.estado == EstadoEjecucion.CANCELADO


# ── TestPendingSync ───────────────────────────────────────────────────────────


class TestPendingSync:
    def test_pending_eliminado_al_completar(
        self, sincronizador: SincronizadorServicio, pending: PendingSyncStorage, tmp_path
    ) -> None:
        origen = tmp_path / "origen"
        destino = tmp_path / "destino"
        origen.mkdir(); destino.mkdir()

        resultado = sincronizador.ejecutar(
            _plan([], str(origen), str(destino)), threading.Event(), modo_prueba=True
        )
        assert resultado.estado == EstadoEjecucion.COMPLETADO
        assert not pending.existe()

    def test_pending_guardado_antes_de_operar(
        self, pending: PendingSyncStorage, log: LogServicio, tmp_path
    ) -> None:
        """El pending se crea al inicio de ejecutar."""
        origen = tmp_path / "origen"
        destino = tmp_path / "destino"
        origen.mkdir(); destino.mkdir()

        check_pendiente: list[bool] = []

        class IntercepPending(PendingSyncStorage):
            def guardar(self, p):
                check_pendiente.append(True)
                super().guardar(p)

        pending_intercep = IntercepPending(tmp_path / "pending2_dir")
        sinc2 = SincronizadorServicio(pending_intercep, log)
        sinc2.ejecutar(
            _plan([], str(origen), str(destino)), threading.Event(), modo_prueba=True
        )
        assert len(check_pendiente) >= 1


# ── TestResultadoEjecucion ────────────────────────────────────────────────────


class TestResultadoEjecucion:
    def test_resultado_tiene_uuid(
        self, sincronizador: SincronizadorServicio, tmp_path
    ) -> None:
        origen = tmp_path / "origen"
        destino = tmp_path / "destino"
        origen.mkdir(); destino.mkdir()

        resultado = sincronizador.ejecutar(
            _plan([], str(origen), str(destino)), threading.Event(), modo_prueba=True
        )
        assert len(resultado.id) == 36

    def test_resultado_duracion_no_negativa(
        self, sincronizador: SincronizadorServicio, tmp_path
    ) -> None:
        origen = tmp_path / "origen"
        destino = tmp_path / "destino"
        origen.mkdir(); destino.mkdir()

        resultado = sincronizador.ejecutar(
            _plan([], str(origen), str(destino)), threading.Event(), modo_prueba=True
        )
        assert resultado.duracion_ejecucion >= 0

    def test_resultado_error_en_fallidas(
        self, sincronizador: SincronizadorServicio, tmp_path
    ) -> None:
        origen = tmp_path / "origen"
        destino = tmp_path / "destino"
        origen.mkdir(); destino.mkdir()

        # Operación que fallará: ruta de origen inexistente
        op = OperacionPlanificada(
            tipo=TipoOperacion.COPIAR,
            ruta_origen=str(origen / "no_existe.txt"),
            ruta_destino=str(destino / "no_existe.txt"),
            ruta_relativa="no_existe.txt",
            tamaño=0,
        )
        resultado = sincronizador.ejecutar(
            _plan([op], str(origen), str(destino)), threading.Event()
        )
        assert len(resultado.operaciones_fallidas) == 1
        assert len(resultado.errores) == 1
