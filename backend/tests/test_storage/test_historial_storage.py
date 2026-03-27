"""
Tests de HistorialStorage — persistencia de ejecuciones en data/history/.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pytest

from app.models.enums import EstadoEjecucion, MetodoComparacion
from app.models.plan import ResumenPlan
from app.models.resultado import ResultadoEjecucion
from app.storage.historial_storage import FILE_PREFIX, HistorialStorage


# ── helpers ───────────────────────────────────────────────────────────────────


def _resumen_vacio() -> ResumenPlan:
    return ResumenPlan(
        nuevos=0,
        modificados=0,
        eliminados=0,
        identicos=0,
        excluidos=0,
        errores=0,
        conflictos_nube=0,
        omitidos=0,
        tamaño_copiar=0,
        tamaño_reemplazar=0,
        tamaño_eliminar=0,
        total_elementos=0,
    )


def _resultado(
    resultado_id: str = "run-001",
    estado: EstadoEjecucion = EstadoEjecucion.COMPLETADO,
    timestamp_inicio: str = "2026-03-27T10:00:00+00:00",
    timestamp_fin: str = "2026-03-27T10:01:00+00:00",
) -> ResultadoEjecucion:
    return ResultadoEjecucion(
        id=resultado_id,
        plan_id="plan-001",
        perfil_id="perfil-001",
        origen="C:/origen",
        destino="D:/destino",
        metodo_comparacion=MetodoComparacion.TAMAÑO_FECHA,
        reglas_activas=[],
        estado=estado,
        modo_prueba=False,
        resumen=_resumen_vacio(),
        operaciones_completadas=[],
        operaciones_fallidas=[],
        errores=[],
        reintentos=[],
        duracion_analisis=1.0,
        duracion_ejecucion=2.5,
        timestamp_inicio=timestamp_inicio,
        timestamp_fin=timestamp_fin,
        version_esquema=1,
    )


def _storage(tmp_path: Path) -> HistorialStorage:
    return HistorialStorage(tmp_path)


# ── TestHistorialStorageGuardar ───────────────────────────────────────────────


class TestHistorialStorageGuardar:
    def test_crea_archivo(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        r = _resultado("abc123")
        storage.guardar(r)
        assert (tmp_path / "history" / "run_abc123.json").exists()

    def test_nombre_de_archivo_correcto(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        storage.guardar(_resultado("mi-id"))
        archivos = list((tmp_path / "history").glob("run_*.json"))
        assert len(archivos) == 1
        assert archivos[0].name == "run_mi-id.json"

    def test_contenido_es_json_valido(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        storage.guardar(_resultado("r1"))
        texto = (tmp_path / "history" / "run_r1.json").read_text(encoding="utf-8")
        datos = json.loads(texto)
        assert datos["id"] == "r1"

    def test_sobrescribe_mismo_id(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        r1 = _resultado("id1", estado=EstadoEjecucion.COMPLETADO)
        storage.guardar(r1)
        r2 = _resultado("id1", estado=EstadoEjecucion.FALLIDO)
        storage.guardar(r2)

        leido = storage.obtener("id1")
        assert leido is not None
        assert leido.estado == EstadoEjecucion.FALLIDO


# ── TestHistorialStorageRotacion ──────────────────────────────────────────────


class TestHistorialStorageRotacion:
    def _crear_con_mtime(
        self, storage: HistorialStorage, resultado_id: str, mtime: float
    ) -> None:
        """Guarda un resultado y ajusta el mtime del archivo para controlar el orden."""
        r = _resultado(resultado_id)
        storage.guardar(r, limite=0)  # sin límite para no rotar durante la creación
        ruta = storage._dir / f"{FILE_PREFIX}{resultado_id}.json"
        os.utime(ruta, (mtime, mtime))

    def test_rotacion_elimina_mas_antiguos(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        t_base = 1_000_000.0
        # Crear 5 registros con mtime incremental (el primero es el más antiguo)
        for i in range(5):
            self._crear_con_mtime(storage, f"id-{i}", t_base + i)

        # Guardar uno más con límite 3 → deben quedar solo 3 (los más recientes)
        r = _resultado("id-5")
        storage.guardar(r, limite=3)
        # Se ajusta el mtime del último para que sea el más reciente
        ruta = storage._dir / "run_id-5.json"
        os.utime(ruta, (t_base + 5, t_base + 5))

        assert storage.contar() == 3

    def test_rotacion_conserva_mas_recientes(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        t_base = 2_000_000.0
        for i in range(4):
            self._crear_con_mtime(storage, f"r-{i}", t_base + i)

        # Guardar con límite 2
        r = _resultado("r-4")
        storage.guardar(r, limite=2)
        os.utime(storage._dir / "run_r-4.json", (t_base + 4, t_base + 4))

        # Solo deben existir los 2 más recientes
        archivos = [p.stem for p in storage._dir.glob("run_*.json")]
        assert len(archivos) == 2
        # Los más recientes son r-3 y r-4
        assert "run_r-3" in archivos
        assert "run_r-4" in archivos

    def test_limite_cero_no_rota(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        for i in range(10):
            storage.guardar(_resultado(f"sin-rotar-{i}"), limite=0)
        assert storage.contar() == 10

    def test_limite_negativo_no_rota(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        for i in range(5):
            storage.guardar(_resultado(f"neg-{i}"), limite=-1)
        assert storage.contar() == 5

    def test_guardar_dentro_de_limite_no_borra(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        for i in range(3):
            storage.guardar(_resultado(f"ok-{i}"), limite=5)
        assert storage.contar() == 3


# ── TestHistorialStorageListar ────────────────────────────────────────────────


class TestHistorialStorageListar:
    def test_listar_vacio(self, tmp_path: Path) -> None:
        assert _storage(tmp_path).listar() == []

    def test_listar_una_entrada(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        storage.guardar(_resultado("unico"))
        lista = storage.listar()
        assert len(lista) == 1
        assert lista[0]["id"] == "unico"

    def test_listar_contiene_campos_cabecera(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        storage.guardar(_resultado("h1"))
        entrada = storage.listar()[0]
        assert "id" in entrada
        assert "perfil_id" in entrada
        assert "estado" in entrada
        assert "timestamp_inicio" in entrada
        assert "timestamp_fin" in entrada

    def test_listar_ordena_mas_reciente_primero(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        t_base = 3_000_000.0

        for i in range(3):
            r = _resultado(f"ord-{i}")
            storage.guardar(r, limite=0)
            ruta = storage._dir / f"run_ord-{i}.json"
            os.utime(ruta, (t_base + i, t_base + i))

        lista = storage.listar()
        ids = [e["id"] for e in lista]
        # El más reciente (ord-2) debe aparecer primero
        assert ids[0] == "ord-2"
        assert ids[-1] == "ord-0"

    def test_listar_omite_archivos_corruptos(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        storage.guardar(_resultado("valido"))
        (storage._dir / "run_corrupto.json").write_text("{basura", encoding="utf-8")
        lista = storage.listar()
        assert len(lista) == 1
        assert lista[0]["id"] == "valido"


# ── TestHistorialStorageObtener ───────────────────────────────────────────────


class TestHistorialStorageObtener:
    def test_obtener_existente(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        storage.guardar(_resultado("ex-1"))
        r = storage.obtener("ex-1")
        assert r is not None
        assert r.id == "ex-1"
        assert r.estado == EstadoEjecucion.COMPLETADO

    def test_obtener_no_existente_retorna_none(self, tmp_path: Path) -> None:
        assert _storage(tmp_path).obtener("fantasma") is None

    def test_obtener_json_corrupto_retorna_none(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        (storage._dir / "run_malformado.json").write_text("no es json", encoding="utf-8")
        assert storage.obtener("malformado") is None

    def test_obtener_round_trip_completo(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        original = _resultado(
            "rt-1",
            estado=EstadoEjecucion.COMPLETADO_CON_ERRORES,
            timestamp_inicio="2026-01-01T08:00:00+00:00",
            timestamp_fin="2026-01-01T08:30:00+00:00",
        )
        storage.guardar(original)
        recuperado = storage.obtener("rt-1")

        assert recuperado is not None
        assert recuperado.id == original.id
        assert recuperado.estado == original.estado
        assert recuperado.timestamp_inicio == original.timestamp_inicio
        assert recuperado.duracion_ejecucion == original.duracion_ejecucion


# ── TestHistorialStorageEliminar ──────────────────────────────────────────────


class TestHistorialStorageEliminar:
    def test_eliminar_existente_retorna_true(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        storage.guardar(_resultado("borra-me"))
        assert storage.eliminar("borra-me") is True

    def test_eliminar_borra_el_archivo(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        storage.guardar(_resultado("del-1"))
        storage.eliminar("del-1")
        assert not (storage._dir / "run_del-1.json").exists()

    def test_eliminar_no_existente_retorna_false(self, tmp_path: Path) -> None:
        assert _storage(tmp_path).eliminar("no-existe") is False

    def test_eliminar_doble_no_falla(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        storage.guardar(_resultado("doble"))
        storage.eliminar("doble")
        assert storage.eliminar("doble") is False


# ── TestHistorialStorageContar ────────────────────────────────────────────────


class TestHistorialStorageContar:
    def test_contar_vacio(self, tmp_path: Path) -> None:
        assert _storage(tmp_path).contar() == 0

    def test_contar_tres(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        for i in range(3):
            storage.guardar(_resultado(f"cnt-{i}"))
        assert storage.contar() == 3

    def test_contar_disminuye_tras_eliminar(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        for i in range(4):
            storage.guardar(_resultado(f"c-{i}"))
        storage.eliminar("c-0")
        assert storage.contar() == 3

    def test_crea_directorio_history(self, tmp_path: Path) -> None:
        """HistorialStorage crea data/history/ al inicializarse."""
        _storage(tmp_path)
        assert (tmp_path / "history").is_dir()
