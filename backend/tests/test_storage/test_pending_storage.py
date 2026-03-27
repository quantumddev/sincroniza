"""
Tests de PendingSyncStorage — gestión de pending_sync.json.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.models.configuracion import PendingSync
from app.storage.pending_storage import PENDING_FILE, PendingSyncStorage


# ── helpers ───────────────────────────────────────────────────────────────────


def _storage(tmp_path: Path) -> PendingSyncStorage:
    return PendingSyncStorage(tmp_path)


def _pending(
    plan_id: str = "plan-001",
    completadas: list[str] | None = None,
    pendientes: list[str] | None = None,
) -> PendingSync:
    return PendingSync(
        plan_id=plan_id,
        perfil_id="perfil-001",
        timestamp_inicio="2026-03-27T09:00:00+00:00",
        operaciones_completadas=completadas if completadas is not None else [],
        operaciones_pendientes=pendientes if pendientes is not None else ["archivo1.txt", "archivo2.txt"],
    )


# ── TestPendingSyncStorageExiste ──────────────────────────────────────────────


class TestPendingSyncStorageExiste:
    def test_false_si_no_hay_archivo(self, tmp_path: Path) -> None:
        assert _storage(tmp_path).existe() is False

    def test_true_tras_guardar(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        storage.guardar(_pending())
        assert storage.existe() is True

    def test_false_tras_eliminar(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        storage.guardar(_pending())
        storage.eliminar()
        assert storage.existe() is False


# ── TestPendingSyncStorageGuardar ─────────────────────────────────────────────


class TestPendingSyncStorageGuardar:
    def test_crea_archivo(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        storage.guardar(_pending())
        assert (tmp_path / PENDING_FILE).exists()

    def test_nombre_de_archivo_correcto(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        storage.guardar(_pending())
        assert storage.ruta.name == PENDING_FILE

    def test_contenido_es_utf8(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        storage.guardar(_pending(pendientes=["ruta/con/acentos/ñoño.txt"]))
        texto = (tmp_path / PENDING_FILE).read_text(encoding="utf-8")
        assert "ñoño" in texto

    def test_crea_directorio_padre(self, tmp_path: Path) -> None:
        nested = tmp_path / "sub" / "data"
        storage = PendingSyncStorage(nested)
        storage.guardar(_pending())
        assert (nested / PENDING_FILE).exists()

    def test_sobrescribe_estado_anterior(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        storage.guardar(_pending("plan-A"))
        storage.guardar(_pending("plan-B"))
        leido = storage.leer()
        assert leido is not None
        assert leido.plan_id == "plan-B"


# ── TestPendingSyncStorageLeer ────────────────────────────────────────────────


class TestPendingSyncStorageLeer:
    def test_retorna_none_si_no_existe(self, tmp_path: Path) -> None:
        assert _storage(tmp_path).leer() is None

    def test_retorna_none_si_json_corrupto(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        (tmp_path / PENDING_FILE).write_text("{no es json", encoding="utf-8")
        assert storage.leer() is None

    def test_retorna_none_si_campos_faltantes(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        (tmp_path / PENDING_FILE).write_text('{"plan_id": "x"}', encoding="utf-8")
        assert storage.leer() is None

    def test_round_trip_basico(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        original = _pending()
        storage.guardar(original)
        leido = storage.leer()

        assert leido is not None
        assert leido.plan_id == original.plan_id
        assert leido.perfil_id == original.perfil_id
        assert leido.timestamp_inicio == original.timestamp_inicio

    def test_round_trip_listas(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        original = _pending(
            completadas=["docs/a.txt", "docs/b.txt"],
            pendientes=["src/c.py", "src/d.py", "src/e.py"],
        )
        storage.guardar(original)
        leido = storage.leer()

        assert leido is not None
        assert leido.operaciones_completadas == ["docs/a.txt", "docs/b.txt"]
        assert leido.operaciones_pendientes == ["src/c.py", "src/d.py", "src/e.py"]

    def test_round_trip_listas_vacias(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        original = _pending(completadas=[], pendientes=[])
        storage.guardar(original)
        leido = storage.leer()

        assert leido is not None
        assert leido.operaciones_completadas == []
        assert leido.operaciones_pendientes == []


# ── TestPendingSyncStorageEliminar ────────────────────────────────────────────


class TestPendingSyncStorageEliminar:
    def test_retorna_true_si_existia(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        storage.guardar(_pending())
        assert storage.eliminar() is True

    def test_archivo_desaparece_tras_eliminar(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        storage.guardar(_pending())
        storage.eliminar()
        assert not (tmp_path / PENDING_FILE).exists()

    def test_retorna_false_si_no_existia(self, tmp_path: Path) -> None:
        assert _storage(tmp_path).eliminar() is False

    def test_eliminar_doble_no_falla(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        storage.guardar(_pending())
        storage.eliminar()
        assert storage.eliminar() is False

    def test_leer_despues_de_eliminar_retorna_none(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        storage.guardar(_pending())
        storage.eliminar()
        assert storage.leer() is None


# ── TestPendingSyncStorageRuta ────────────────────────────────────────────────


class TestPendingSyncStorageRuta:
    def test_ruta_property_apunta_a_archivo_correcto(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        assert storage.ruta == tmp_path / PENDING_FILE
