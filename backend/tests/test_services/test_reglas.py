"""
Tests para ReglasServicio.

Verifica CRUD de reglas de usuario, protección de reglas del sistema,
evaluación glob y validación de patrones.
"""

from __future__ import annotations

import pytest

from app.models.enums import OrigenRegla, TipoRegla
from app.models.regla import Regla
from app.services.reglas import ReglasServicio
from app.storage.config_storage import ConfigStorage


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture()
def storage(tmp_path) -> ConfigStorage:
    return ConfigStorage(tmp_path)


@pytest.fixture()
def servicio(storage) -> ReglasServicio:
    return ReglasServicio(storage)


def _regla_sistema(patron: str = "*.sys") -> Regla:
    return Regla(
        id="sys-1",
        patron=patron,
        tipo=TipoRegla.ARCHIVO,
        activa=True,
        origen=OrigenRegla.SISTEMA,
    )


def _insertar_regla_sistema(storage: ConfigStorage, regla: Regla) -> None:
    config = storage.leer()
    config.reglas_exclusion.append(regla)
    storage.escribir(config)


# ── TestListarObtener ─────────────────────────────────────────────────────────


class TestListarObtener:
    def test_lista_vacia_sin_reglas(self, servicio: ReglasServicio) -> None:
        assert servicio.listar() == []

    def test_lista_reglas_existentes(self, storage, servicio: ReglasServicio) -> None:
        _insertar_regla_sistema(storage, _regla_sistema())
        creada = servicio.crear("*.log", TipoRegla.ARCHIVO)
        resultado = servicio.listar()
        assert len(resultado) == 2
        ids = {r.id for r in resultado}
        assert "sys-1" in ids
        assert creada.id in ids

    def test_obtener_existente(self, servicio: ReglasServicio) -> None:
        creada = servicio.crear("*.tmp", TipoRegla.ARCHIVO)
        obtenida = servicio.obtener(creada.id)
        assert obtenida is not None
        assert obtenida.id == creada.id

    def test_obtener_no_existente(self, servicio: ReglasServicio) -> None:
        assert servicio.obtener("no-existe") is None


# ── TestCrear ─────────────────────────────────────────────────────────────────


class TestCrear:
    def test_crear_regla_usuario(self, servicio: ReglasServicio) -> None:
        regla = servicio.crear("*.log", TipoRegla.ARCHIVO)
        assert regla.patron == "*.log"
        assert regla.tipo == TipoRegla.ARCHIVO
        assert regla.activa is True
        assert regla.origen == OrigenRegla.USUARIO

    def test_crear_genera_uuid(self, servicio: ReglasServicio) -> None:
        r1 = servicio.crear("*.log", TipoRegla.ARCHIVO)
        r2 = servicio.crear("*.tmp", TipoRegla.ARCHIVO)
        assert r1.id != r2.id
        assert len(r1.id) == 36  # UUID4 canónico

    def test_crear_activa_falsa(self, servicio: ReglasServicio) -> None:
        regla = servicio.crear("*.bak", TipoRegla.ARCHIVO, activa=False)
        assert regla.activa is False

    def test_crear_patron_invalido_vacio(self, servicio: ReglasServicio) -> None:
        with pytest.raises(ValueError):
            servicio.crear("", TipoRegla.ARCHIVO)

    def test_crear_patron_invalido_espacios(self, servicio: ReglasServicio) -> None:
        with pytest.raises(ValueError):
            servicio.crear("   ", TipoRegla.ARCHIVO)

    def test_crear_persiste(self, storage, servicio: ReglasServicio) -> None:
        regla = servicio.crear("*.log", TipoRegla.ARCHIVO)
        nuevo_servicio = ReglasServicio(storage)
        assert nuevo_servicio.obtener(regla.id) is not None

    def test_crear_tipo_carpeta(self, servicio: ReglasServicio) -> None:
        regla = servicio.crear("node_modules", TipoRegla.CARPETA)
        assert regla.tipo == TipoRegla.CARPETA

    def test_crear_patron_con_doble_asterisco(self, servicio: ReglasServicio) -> None:
        regla = servicio.crear("dist/**", TipoRegla.ARCHIVO)
        assert regla.patron == "dist/**"


# ── TestActualizar ────────────────────────────────────────────────────────────


class TestActualizar:
    def test_actualizar_activa(self, servicio: ReglasServicio) -> None:
        regla = servicio.crear("*.log", TipoRegla.ARCHIVO, activa=True)
        actualizada = servicio.actualizar(regla.id, {"activa": False})
        assert actualizada.activa is False

    def test_actualizar_patron(self, servicio: ReglasServicio) -> None:
        regla = servicio.crear("*.log", TipoRegla.ARCHIVO)
        actualizada = servicio.actualizar(regla.id, {"patron": "*.txt"})
        assert actualizada.patron == "*.txt"

    def test_actualizar_patron_invalido(self, servicio: ReglasServicio) -> None:
        regla = servicio.crear("*.log", TipoRegla.ARCHIVO)
        with pytest.raises(ValueError):
            servicio.actualizar(regla.id, {"patron": ""})

    def test_actualizar_persiste(self, storage, servicio: ReglasServicio) -> None:
        regla = servicio.crear("*.log", TipoRegla.ARCHIVO, activa=True)
        servicio.actualizar(regla.id, {"activa": False})
        nuevo_servicio = ReglasServicio(storage)
        refresco = nuevo_servicio.obtener(regla.id)
        assert refresco is not None
        assert refresco.activa is False

    def test_actualizar_no_existente(self, servicio: ReglasServicio) -> None:
        with pytest.raises(KeyError):
            servicio.actualizar("no-existe", {"activa": False})


# ── TestEliminar ──────────────────────────────────────────────────────────────


class TestEliminar:
    def test_eliminar_regla_usuario(self, servicio: ReglasServicio) -> None:
        regla = servicio.crear("*.log", TipoRegla.ARCHIVO)
        resultado = servicio.eliminar(regla.id)
        assert resultado is True
        assert servicio.obtener(regla.id) is None

    def test_eliminar_retorna_false_si_no_existe(self, servicio: ReglasServicio) -> None:
        assert servicio.eliminar("no-existe") is False

    def test_eliminar_regla_sistema_prohibido(
        self, storage, servicio: ReglasServicio
    ) -> None:
        _insertar_regla_sistema(storage, _regla_sistema())
        with pytest.raises(PermissionError):
            servicio.eliminar("sys-1")

    def test_eliminar_persiste(self, storage, servicio: ReglasServicio) -> None:
        regla = servicio.crear("*.log", TipoRegla.ARCHIVO)
        servicio.eliminar(regla.id)
        nuevo_servicio = ReglasServicio(storage)
        assert nuevo_servicio.obtener(regla.id) is None


# ── TestEvaluar ───────────────────────────────────────────────────────────────


class TestEvaluar:
    def test_evaluar_sin_reglas(self, servicio: ReglasServicio) -> None:
        assert servicio.evaluar("archivo.log", es_carpeta=False) is None

    def test_evaluar_coincide(self, servicio: ReglasServicio) -> None:
        regla = servicio.crear("*.log", TipoRegla.ARCHIVO, activa=True)
        resultado = servicio.evaluar("debug.log", es_carpeta=False)
        assert resultado is not None
        assert resultado.id == regla.id

    def test_evaluar_no_coincide(self, servicio: ReglasServicio) -> None:
        servicio.crear("*.log", TipoRegla.ARCHIVO, activa=True)
        assert servicio.evaluar("debug.txt", es_carpeta=False) is None

    def test_evaluar_regla_inactiva_no_aplica(self, servicio: ReglasServicio) -> None:
        servicio.crear("*.log", TipoRegla.ARCHIVO, activa=False)
        assert servicio.evaluar("debug.log", es_carpeta=False) is None

    def test_evaluar_tipo_carpeta(self, servicio: ReglasServicio) -> None:
        regla = servicio.crear("node_modules", TipoRegla.CARPETA, activa=True)
        resultado = servicio.evaluar("node_modules", es_carpeta=True)
        assert resultado is not None
        assert resultado.id == regla.id


# ── TestValidarPatron ─────────────────────────────────────────────────────────


class TestValidarPatron:
    def test_patron_simple(self) -> None:
        assert ReglasServicio.validar_patron("*.log") is True

    def test_patron_doble_asterisco(self) -> None:
        assert ReglasServicio.validar_patron("dist/**") is True

    def test_patron_vacio(self) -> None:
        assert ReglasServicio.validar_patron("") is False

    def test_patron_solo_espacios(self) -> None:
        assert ReglasServicio.validar_patron("   ") is False

    def test_patron_path_relativo(self) -> None:
        assert ReglasServicio.validar_patron("src/*.ts") is True

    def test_patron_interrogacion(self) -> None:
        assert ReglasServicio.validar_patron("fil?.txt") is True

    def test_patron_carpeta_compleja(self) -> None:
        assert ReglasServicio.validar_patron("**/__pycache__/**") is True
