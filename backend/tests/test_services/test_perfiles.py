"""
Tests para PerfilServicio.

Verifica CRUD de perfiles, generación de UUIDs, herencia de defaults del config
y actualización de última ejecución.
"""

from __future__ import annotations

import pytest

from app.models.enums import MetodoComparacion
from app.services.perfiles import PerfilServicio
from app.storage.config_storage import ConfigStorage


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture()
def storage(tmp_path) -> ConfigStorage:
    return ConfigStorage(tmp_path)


@pytest.fixture()
def servicio(storage) -> PerfilServicio:
    return PerfilServicio(storage)


def _crear_perfil(servicio: PerfilServicio, nombre: str = "Mi perfil"):
    return servicio.crear(
        nombre=nombre,
        origen="/ruta/origen",
        destino="/ruta/destino",
    )


# ── TestListarObtener ─────────────────────────────────────────────────────────


class TestListarObtener:
    def test_listar_vacio(self, servicio: PerfilServicio) -> None:
        assert servicio.listar() == []

    def test_listar_varios(self, servicio: PerfilServicio) -> None:
        _crear_perfil(servicio, "A")
        _crear_perfil(servicio, "B")
        assert len(servicio.listar()) == 2

    def test_obtener_existente(self, servicio: PerfilServicio) -> None:
        perfil = _crear_perfil(servicio)
        obtenido = servicio.obtener(perfil.id)
        assert obtenido is not None
        assert obtenido.id == perfil.id

    def test_obtener_no_existente(self, servicio: PerfilServicio) -> None:
        assert servicio.obtener("no-existe") is None


# ── TestCrear ─────────────────────────────────────────────────────────────────


class TestCrear:
    def test_crear_campos_basicos(self, servicio: PerfilServicio) -> None:
        perfil = servicio.crear("Test", "/src", "/dst")
        assert perfil.nombre == "Test"
        assert perfil.origen == "/src"
        assert perfil.destino == "/dst"

    def test_crear_uuid_unico(self, servicio: PerfilServicio) -> None:
        p1 = _crear_perfil(servicio, "A")
        p2 = _crear_perfil(servicio, "B")
        assert p1.id != p2.id
        assert len(p1.id) == 36

    def test_crear_ultima_ejecucion_none(self, servicio: PerfilServicio) -> None:
        perfil = _crear_perfil(servicio)
        assert perfil.ultima_ejecucion is None

    def test_crear_creado_no_vacio(self, servicio: PerfilServicio) -> None:
        perfil = _crear_perfil(servicio)
        assert perfil.creado and isinstance(perfil.creado, str)

    def test_crear_defaults_de_config(self, storage, servicio: PerfilServicio) -> None:
        config = storage.leer()
        perfil = _crear_perfil(servicio)
        assert perfil.umbral_eliminaciones == config.umbral_eliminaciones
        assert perfil.timeout_por_archivo == config.timeout_por_archivo
        assert perfil.metodo_comparacion == config.metodo_comparacion_defecto

    def test_crear_sobrescribe_defaults(self, servicio: PerfilServicio) -> None:
        perfil = servicio.crear(
            "Test",
            "/src",
            "/dst",
            metodo_comparacion=MetodoComparacion.HASH,
            umbral_eliminaciones=5,
            timeout_por_archivo=120,
        )
        assert perfil.metodo_comparacion == MetodoComparacion.HASH
        assert perfil.umbral_eliminaciones == 5
        assert perfil.timeout_por_archivo == 120

    def test_crear_reglas_vacias_por_defecto(self, servicio: PerfilServicio) -> None:
        perfil = _crear_perfil(servicio)
        assert perfil.reglas_exclusion_ids == []
        assert perfil.reglas_propias == []

    def test_crear_persiste(self, storage, servicio: PerfilServicio) -> None:
        perfil = _crear_perfil(servicio)
        nuevo_servicio = PerfilServicio(storage)
        assert nuevo_servicio.obtener(perfil.id) is not None


# ── TestActualizar ────────────────────────────────────────────────────────────


class TestActualizar:
    def test_actualizar_nombre(self, servicio: PerfilServicio) -> None:
        perfil = _crear_perfil(servicio, "Original")
        actualizado = servicio.actualizar(perfil.id, {"nombre": "Actualizado"})
        assert actualizado.nombre == "Actualizado"

    def test_actualizar_origen(self, servicio: PerfilServicio) -> None:
        perfil = _crear_perfil(servicio)
        actualizado = servicio.actualizar(perfil.id, {"origen": "/nuevo"})
        assert actualizado.origen == "/nuevo"

    def test_actualizar_persiste(self, storage, servicio: PerfilServicio) -> None:
        perfil = _crear_perfil(servicio, "Viejo")
        servicio.actualizar(perfil.id, {"nombre": "Nuevo"})
        nuevo_servicio = PerfilServicio(storage)
        assert nuevo_servicio.obtener(perfil.id).nombre == "Nuevo"

    def test_actualizar_no_existente(self, servicio: PerfilServicio) -> None:
        with pytest.raises(KeyError):
            servicio.actualizar("no-existe", {"nombre": "X"})


# ── TestEliminar ──────────────────────────────────────────────────────────────


class TestEliminar:
    def test_eliminar_existente(self, servicio: PerfilServicio) -> None:
        perfil = _crear_perfil(servicio)
        assert servicio.eliminar(perfil.id) is True
        assert servicio.obtener(perfil.id) is None

    def test_eliminar_no_existente(self, servicio: PerfilServicio) -> None:
        assert servicio.eliminar("no-existe") is False

    def test_eliminar_persiste(self, storage, servicio: PerfilServicio) -> None:
        perfil = _crear_perfil(servicio)
        servicio.eliminar(perfil.id)
        nuevo_servicio = PerfilServicio(storage)
        assert nuevo_servicio.obtener(perfil.id) is None


# ── TestActualizarUltimaEjecucion ─────────────────────────────────────────────


class TestActualizarUltimaEjecucion:
    def test_actualizar_con_timestamp_explicitoo(
        self, servicio: PerfilServicio
    ) -> None:
        perfil = _crear_perfil(servicio)
        ts = "2024-06-01T12:00:00"
        actualizado = servicio.actualizar_ultima_ejecucion(perfil.id, ts)
        assert actualizado.ultima_ejecucion == ts

    def test_actualizar_sin_timestamp_usa_ahora(
        self, servicio: PerfilServicio
    ) -> None:
        perfil = _crear_perfil(servicio)
        actualizado = servicio.actualizar_ultima_ejecucion(perfil.id)
        assert actualizado.ultima_ejecucion is not None
        assert isinstance(actualizado.ultima_ejecucion, str)

    def test_actualizar_persiste(
        self, storage, servicio: PerfilServicio
    ) -> None:
        perfil = _crear_perfil(servicio)
        ts = "2024-06-01T12:00:00"
        servicio.actualizar_ultima_ejecucion(perfil.id, ts)
        nuevo_servicio = PerfilServicio(storage)
        assert nuevo_servicio.obtener(perfil.id).ultima_ejecucion == ts

    def test_actualizar_no_existente(self, servicio: PerfilServicio) -> None:
        with pytest.raises(KeyError):
            servicio.actualizar_ultima_ejecucion("no-existe")
