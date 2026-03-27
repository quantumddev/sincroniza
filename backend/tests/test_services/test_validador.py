"""
Tests de ValidadorServicio.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.models.enums import MetodoComparacion
from app.models.nodo_arbol import NodoArbol
from app.models.enums import EstadoNodo, TipoElemento
from app.models.plan import PlanSincronizacion, ResumenPlan
from app.core.fingerprint import calcular_fingerprint
from app.storage.config_storage import ConfigStorage
from app.services.validador import ValidadorServicio


# ── helpers ───────────────────────────────────────────────────────────────────


def _storage(tmp_path: Path) -> ConfigStorage:
    return ConfigStorage(tmp_path)


def _svc(tmp_path: Path) -> ValidadorServicio:
    return ValidadorServicio(_storage(tmp_path))


def _resumen_vacio() -> ResumenPlan:
    return ResumenPlan(
        nuevos=0, modificados=0, eliminados=0, identicos=0,
        excluidos=0, errores=0, conflictos_nube=0, omitidos=0,
        tamaño_copiar=0, tamaño_reemplazar=0, tamaño_eliminar=0, total_elementos=0,
    )


def _plan(origen: str, destino: str, reglas: list[str] | None = None) -> PlanSincronizacion:
    reglas = reglas or []
    metodo = MetodoComparacion.TAMAÑO_FECHA
    fp = calcular_fingerprint(origen, destino, reglas, metodo)
    raiz = NodoArbol(
        nombre=".",
        ruta_relativa=".",
        tipo=TipoElemento.CARPETA,
        estado=EstadoNodo.IDENTICO,
        tamaño=0,
        tamaño_destino=0,
        motivo=None,
    )
    return PlanSincronizacion(
        id="plan-test",
        perfil_id="perfil-test",
        origen=origen,
        destino=destino,
        metodo_comparacion=metodo,
        reglas_activas=list(reglas),
        arbol=raiz,
        operaciones=[],
        resumen=_resumen_vacio(),
        fingerprint=fp,
        mtime_origen=1_000_000.0,
        mtime_destino=2_000_000.0,
        timestamp="2026-03-27T10:00:00+00:00",
    )


# ── TestValidarRutas ──────────────────────────────────────────────────────────


class TestValidarRutas:
    def test_rutas_validas(self, tmp_path: Path) -> None:
        svc = _svc(tmp_path)
        origen = tmp_path / "a"
        destino = tmp_path / "b"
        origen.mkdir()
        destino.mkdir()
        valido, errores = svc.validar_rutas(str(origen), str(destino))
        assert valido is True
        assert errores == []

    def test_origen_no_existe(self, tmp_path: Path) -> None:
        svc = _svc(tmp_path)
        destino = tmp_path / "b"
        destino.mkdir()
        valido, errores = svc.validar_rutas(str(tmp_path / "no_existe"), str(destino))
        assert valido is False
        assert any("origen" in e.lower() for e in errores)

    def test_destino_no_existe(self, tmp_path: Path) -> None:
        svc = _svc(tmp_path)
        origen = tmp_path / "a"
        origen.mkdir()
        valido, errores = svc.validar_rutas(str(origen), str(tmp_path / "no_existe"))
        assert valido is False
        assert any("destino" in e.lower() for e in errores)

    def test_mismo_directorio(self, tmp_path: Path) -> None:
        svc = _svc(tmp_path)
        origen = tmp_path / "a"
        origen.mkdir()
        valido, errores = svc.validar_rutas(str(origen), str(origen))
        assert valido is False
        assert any("misma ruta" in e.lower() for e in errores)

    def test_destino_dentro_de_origen(self, tmp_path: Path) -> None:
        svc = _svc(tmp_path)
        origen = tmp_path / "raiz"
        destino = origen / "sub"
        origen.mkdir()
        destino.mkdir()
        valido, errores = svc.validar_rutas(str(origen), str(destino))
        assert valido is False
        assert len(errores) > 0

    def test_origen_dentro_de_destino(self, tmp_path: Path) -> None:
        svc = _svc(tmp_path)
        destino = tmp_path / "raiz"
        origen = destino / "sub"
        destino.mkdir()
        origen.mkdir()
        valido, errores = svc.validar_rutas(str(origen), str(destino))
        assert valido is False

    def test_restricciones_origen_fuera_de_lista(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        config = storage.leer()
        config.restricciones_ruta["origen_permitido"] = ["C:/permitido"]
        storage.escribir(config)

        origen = tmp_path / "a"
        destino = tmp_path / "b"
        origen.mkdir()
        destino.mkdir()
        svc = ValidadorServicio(storage)
        valido, errores = svc.validar_rutas(str(origen), str(destino))
        assert valido is False
        assert any("origen" in e.lower() for e in errores)

    def test_restricciones_vacias_permiten_todo(self, tmp_path: Path) -> None:
        svc = _svc(tmp_path)
        origen = tmp_path / "a"
        destino = tmp_path / "b"
        origen.mkdir()
        destino.mkdir()
        # Con restricciones vacías (default) → debe pasar
        valido, _ = svc.validar_rutas(str(origen), str(destino))
        assert valido is True

    def test_multiples_errores_acumulados(self, tmp_path: Path) -> None:
        svc = _svc(tmp_path)
        # Ninguno de los dos existe
        valido, errores = svc.validar_rutas("/no/existe/a", "/no/existe/b")
        assert valido is False
        assert len(errores) >= 2


# ── TestVerificarFingerprint ──────────────────────────────────────────────────


class TestVerificarFingerprint:
    def test_fingerprint_correcto(self, tmp_path: Path) -> None:
        svc = _svc(tmp_path)
        plan = _plan("C:/origen", "D:/destino")
        assert svc.verificar_fingerprint(plan) is True

    def test_fingerprint_alterado(self, tmp_path: Path) -> None:
        svc = _svc(tmp_path)
        plan = _plan("C:/origen", "D:/destino")
        # Corromper el fingerprint del plan
        plan.fingerprint = "0000000000000000000000000000000000000000000000000000000000000000"
        assert svc.verificar_fingerprint(plan) is False

    def test_rutas_distintas_dan_fingerprint_distinto(self, tmp_path: Path) -> None:
        svc = _svc(tmp_path)
        plan_a = _plan("C:/a", "D:/d")
        plan_b = _plan("C:/b", "D:/d")
        # Ambos fingerpints son correctos para su propio plan
        assert svc.verificar_fingerprint(plan_a) is True
        assert svc.verificar_fingerprint(plan_b) is True
        # Pero entre sí no son intercambiables
        plan_a.fingerprint = plan_b.fingerprint
        assert svc.verificar_fingerprint(plan_a) is False


# ── TestVerificarMtimeRaiz ────────────────────────────────────────────────────


class TestVerificarMtimeRaiz:
    def test_mtime_no_cambiado(self, tmp_path: Path) -> None:
        svc = _svc(tmp_path)
        origen = tmp_path / "orig"
        destino = tmp_path / "dest"
        origen.mkdir()
        destino.mkdir()

        import os
        mtime_o = os.path.getmtime(str(origen))
        mtime_d = os.path.getmtime(str(destino))

        plan = _plan(str(origen), str(destino))
        plan.mtime_origen = mtime_o
        plan.mtime_destino = mtime_d

        assert svc.verificar_mtime_raiz(plan) is True

    def test_mtime_origen_cambiado(self, tmp_path: Path) -> None:
        svc = _svc(tmp_path)
        origen = tmp_path / "orig2"
        destino = tmp_path / "dest2"
        origen.mkdir()
        destino.mkdir()

        import os
        mtime_d = os.path.getmtime(str(destino))

        plan = _plan(str(origen), str(destino))
        plan.mtime_origen = 0.0       # valor falso → timestamps difieren
        plan.mtime_destino = mtime_d

        assert svc.verificar_mtime_raiz(plan) is False

    def test_directorio_inexistente_retorna_false(self, tmp_path: Path) -> None:
        svc = _svc(tmp_path)
        plan = _plan("/ruta/inexistente/a", "/ruta/inexistente/b")
        assert svc.verificar_mtime_raiz(plan) is False
