"""
Tests para ComparadorServicio.

Verifica clasificación de archivos: NUEVO, MODIFICADO, IDENTICO, ELIMINADO,
EXCLUIDO, CONFLICTO_NUBE, y construcción correcta del resumen y operaciones.
"""

from __future__ import annotations

import os

import pytest

from app.models.enums import (
    EstadoNodo,
    MetodoComparacion,
    OrigenRegla,
    TipoOperacion,
    TipoRegla,
)
from app.models.perfil import Perfil
from app.models.regla import Regla
from app.services.comparador import ComparadorServicio
from app.services.explorador import ExploradorServicio


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture()
def explorador() -> ExploradorServicio:
    return ExploradorServicio()


@pytest.fixture()
def comparador(explorador) -> ComparadorServicio:
    return ComparadorServicio(explorador)


def _perfil(
    tmp_path,
    metodo: MetodoComparacion = MetodoComparacion.TAMAÑO_FECHA,
) -> Perfil:
    return Perfil(
        id="p1",
        nombre="test",
        origen=str(tmp_path / "origen"),
        destino=str(tmp_path / "destino"),
        metodo_comparacion=metodo,
        reglas_exclusion_ids=[],
        reglas_propias=[],
        umbral_eliminaciones=10,
        timeout_por_archivo=30,
        creado="2024-01-01T00:00:00",
        ultima_ejecucion=None,
    )


def _regla(patron: str, tipo: TipoRegla = TipoRegla.ARCHIVO) -> Regla:
    return Regla(
        id=f"r-{patron}",
        patron=patron,
        tipo=tipo,
        activa=True,
        origen=OrigenRegla.USUARIO,
    )


# ── Helpers ───────────────────────────────────────────────────────────────────


def _nodo(plan, estado: EstadoNodo):
    return [n for n in plan.arbol.hijos if n.estado == estado]


def _ops(plan, tipo: TipoOperacion):
    return [op for op in plan.operaciones if op.tipo == tipo]


# ── TestElementoNuevo ─────────────────────────────────────────────────────────


class TestElementoNuevo:
    def test_archivo_nuevo_en_origen(self, comparador, tmp_path) -> None:
        origen = tmp_path / "origen"
        destino = tmp_path / "destino"
        origen.mkdir(); destino.mkdir()
        (origen / "nuevo.txt").write_text("hola")

        plan = comparador.analizar(
            str(origen), str(destino), _perfil(tmp_path), []
        )
        nuevos = _nodo(plan, EstadoNodo.NUEVO)
        assert len(nuevos) == 1
        assert nuevos[0].ruta_relativa == "nuevo.txt"

    def test_archivo_nuevo_genera_op_copiar(self, comparador, tmp_path) -> None:
        origen = tmp_path / "origen"
        destino = tmp_path / "destino"
        origen.mkdir(); destino.mkdir()
        (origen / "a.txt").write_text("x")

        plan = comparador.analizar(str(origen), str(destino), _perfil(tmp_path), [])
        assert len(_ops(plan, TipoOperacion.COPIAR)) == 1

    def test_carpeta_nueva_genera_op_crear_carpeta(self, comparador, tmp_path) -> None:
        origen = tmp_path / "origen"
        destino = tmp_path / "destino"
        origen.mkdir(); destino.mkdir()
        (origen / "sub").mkdir()

        plan = comparador.analizar(str(origen), str(destino), _perfil(tmp_path), [])
        assert len(_ops(plan, TipoOperacion.CREAR_CARPETA)) == 1


# ── TestElementoIdentico ──────────────────────────────────────────────────────


class TestElementoIdentico:
    def test_archivo_identico(self, comparador, tmp_path) -> None:
        origen = tmp_path / "origen"
        destino = tmp_path / "destino"
        origen.mkdir(); destino.mkdir()
        contenido = b"identico"
        (origen / "file.txt").write_bytes(contenido)
        dst = (destino / "file.txt")
        dst.write_bytes(contenido)
        # Igualar mtime exactamente
        mtime = (origen / "file.txt").stat().st_mtime
        os.utime(str(dst), (mtime, mtime))

        plan = comparador.analizar(str(origen), str(destino), _perfil(tmp_path), [])
        identicos = _nodo(plan, EstadoNodo.IDENTICO)
        assert any(n.ruta_relativa == "file.txt" for n in identicos)

    def test_identico_no_genera_operacion(self, comparador, tmp_path) -> None:
        origen = tmp_path / "origen"
        destino = tmp_path / "destino"
        origen.mkdir(); destino.mkdir()
        contenido = b"x"
        (origen / "f.txt").write_bytes(contenido)
        dst = destino / "f.txt"
        dst.write_bytes(contenido)
        mtime = (origen / "f.txt").stat().st_mtime
        os.utime(str(dst), (mtime, mtime))

        plan = comparador.analizar(str(origen), str(destino), _perfil(tmp_path), [])
        assert plan.operaciones == []


# ── TestElementoModificado ────────────────────────────────────────────────────


class TestElementoModificado:
    def test_archivo_modificado_por_tamaño(self, comparador, tmp_path) -> None:
        origen = tmp_path / "origen"
        destino = tmp_path / "destino"
        origen.mkdir(); destino.mkdir()
        (origen / "mod.txt").write_text("aaa")
        (destino / "mod.txt").write_text("bb")

        plan = comparador.analizar(str(origen), str(destino), _perfil(tmp_path), [])
        modificados = _nodo(plan, EstadoNodo.MODIFICADO)
        assert len(modificados) == 1

    def test_modificado_genera_op_reemplazar(self, comparador, tmp_path) -> None:
        origen = tmp_path / "origen"
        destino = tmp_path / "destino"
        origen.mkdir(); destino.mkdir()
        (origen / "mod.txt").write_text("nuevo contenido largo")
        (destino / "mod.txt").write_text("viejo")

        plan = comparador.analizar(str(origen), str(destino), _perfil(tmp_path), [])
        assert len(_ops(plan, TipoOperacion.REEMPLAZAR)) == 1


# ── TestElementoEliminado ─────────────────────────────────────────────────────


class TestElementoEliminado:
    def test_archivo_solo_en_destino_es_eliminado(self, comparador, tmp_path) -> None:
        origen = tmp_path / "origen"
        destino = tmp_path / "destino"
        origen.mkdir(); destino.mkdir()
        (destino / "viejo.txt").write_text("x")

        plan = comparador.analizar(str(origen), str(destino), _perfil(tmp_path), [])
        eliminados = _nodo(plan, EstadoNodo.ELIMINADO)
        assert len(eliminados) == 1

    def test_eliminado_genera_op_eliminar_archivo(self, comparador, tmp_path) -> None:
        origen = tmp_path / "origen"
        destino = tmp_path / "destino"
        origen.mkdir(); destino.mkdir()
        (destino / "viejo.txt").write_text("x")

        plan = comparador.analizar(str(origen), str(destino), _perfil(tmp_path), [])
        assert len(_ops(plan, TipoOperacion.ELIMINAR_ARCHIVO)) == 1

    def test_carpeta_solo_destino_genera_op_eliminar_carpeta(
        self, comparador, tmp_path
    ) -> None:
        origen = tmp_path / "origen"
        destino = tmp_path / "destino"
        origen.mkdir(); destino.mkdir()
        (destino / "orphan").mkdir()

        plan = comparador.analizar(str(origen), str(destino), _perfil(tmp_path), [])
        assert len(_ops(plan, TipoOperacion.ELIMINAR_CARPETA)) == 1


# ── TestElementoExcluido ──────────────────────────────────────────────────────


class TestElementoExcluido:
    def test_archivo_excluido_por_regla(self, comparador, tmp_path) -> None:
        origen = tmp_path / "origen"
        destino = tmp_path / "destino"
        origen.mkdir(); destino.mkdir()
        (origen / "debug.log").write_text("x")

        plan = comparador.analizar(
            str(origen), str(destino), _perfil(tmp_path), [_regla("*.log")]
        )
        excluidos = _nodo(plan, EstadoNodo.EXCLUIDO)
        assert any(n.ruta_relativa == "debug.log" for n in excluidos)

    def test_excluido_no_genera_operacion(self, comparador, tmp_path) -> None:
        origen = tmp_path / "origen"
        destino = tmp_path / "destino"
        origen.mkdir(); destino.mkdir()
        (origen / "debug.log").write_text("x")

        plan = comparador.analizar(
            str(origen), str(destino), _perfil(tmp_path), [_regla("*.log")]
        )
        assert plan.operaciones == []


# ── TestConflictoNube ─────────────────────────────────────────────────────────


class TestConflictoNube:
    def test_archivo_con_conflicto_en_nombre(self, comparador, tmp_path) -> None:
        origen = tmp_path / "origen"
        destino = tmp_path / "destino"
        origen.mkdir(); destino.mkdir()
        (origen / "doc (conflicto de OneDrive).docx").write_text("x")

        plan = comparador.analizar(str(origen), str(destino), _perfil(tmp_path), [])
        conflictos = _nodo(plan, EstadoNodo.CONFLICTO_NUBE)
        assert len(conflictos) == 1

    def test_conflicto_nube_no_genera_operacion(self, comparador, tmp_path) -> None:
        origen = tmp_path / "origen"
        destino = tmp_path / "destino"
        origen.mkdir(); destino.mkdir()
        (origen / "CONFLICTO copia.txt").write_text("x")

        plan = comparador.analizar(str(origen), str(destino), _perfil(tmp_path), [])
        assert plan.operaciones == []


# ── TestResumen ───────────────────────────────────────────────────────────────


class TestResumen:
    def test_resumen_contadores(self, comparador, tmp_path) -> None:
        origen = tmp_path / "origen"
        destino = tmp_path / "destino"
        origen.mkdir(); destino.mkdir()
        (origen / "nuevo.txt").write_text("x")
        (destino / "viejo.txt").write_text("y")

        plan = comparador.analizar(str(origen), str(destino), _perfil(tmp_path), [])
        assert plan.resumen.nuevos == 1
        assert plan.resumen.eliminados == 1
        assert plan.resumen.total_elementos == 2

    def test_resumen_tamaño_copiar(self, comparador, tmp_path) -> None:
        origen = tmp_path / "origen"
        destino = tmp_path / "destino"
        origen.mkdir(); destino.mkdir()
        (origen / "gran.bin").write_bytes(b"a" * 500)

        plan = comparador.analizar(str(origen), str(destino), _perfil(tmp_path), [])
        assert plan.resumen.tamaño_copiar == 500


# ── TestPlanMetadatos ─────────────────────────────────────────────────────────


class TestPlanMetadatos:
    def test_plan_tiene_id_uuid(self, comparador, tmp_path) -> None:
        origen = tmp_path / "origen"
        destino = tmp_path / "destino"
        origen.mkdir(); destino.mkdir()

        plan = comparador.analizar(str(origen), str(destino), _perfil(tmp_path), [])
        assert len(plan.id) == 36

    def test_plan_tiene_fingerprint(self, comparador, tmp_path) -> None:
        origen = tmp_path / "origen"
        destino = tmp_path / "destino"
        origen.mkdir(); destino.mkdir()

        plan = comparador.analizar(str(origen), str(destino), _perfil(tmp_path), [])
        assert plan.fingerprint and len(plan.fingerprint) == 64

    def test_plan_tiene_mtime(self, comparador, tmp_path) -> None:
        origen = tmp_path / "origen"
        destino = tmp_path / "destino"
        origen.mkdir(); destino.mkdir()

        plan = comparador.analizar(str(origen), str(destino), _perfil(tmp_path), [])
        assert plan.mtime_origen > 0
        assert plan.mtime_destino > 0
