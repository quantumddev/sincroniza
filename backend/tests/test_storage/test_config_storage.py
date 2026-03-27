"""
Tests de ConfigStorage — lectura/escritura de settings.json.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.models.configuracion import ConfiguracionApp
from app.models.enums import MetodoComparacion
from app.storage.config_storage import SCHEMA_VERSION, ConfigStorage


# ── helpers ───────────────────────────────────────────────────────────────────


def _storage(tmp_path: Path) -> ConfigStorage:
    return ConfigStorage(tmp_path)


def _config_personalizada() -> ConfiguracionApp:
    return ConfiguracionApp(
        version_esquema=SCHEMA_VERSION,
        tema="oscuro",
        metodo_comparacion_defecto=MetodoComparacion.HASH,
        ultimas_rutas={"origen": "C:/fotos", "destino": "D:/backup"},
        perfiles=[],
        reglas_exclusion=[],
        restricciones_ruta={"origen_permitido": [], "destino_permitido": []},
        umbral_eliminaciones=5,
        timeout_por_archivo=60,
        limite_historial=100,
    )


# ── TestConfigStorageLeer ─────────────────────────────────────────────────────


class TestConfigStorageLeer:
    def test_crea_archivo_si_no_existe(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        settings = tmp_path / "settings.json"

        assert not settings.exists()
        storage.leer()
        assert settings.exists()

    def test_retorna_defecto_si_no_existe(self, tmp_path: Path) -> None:
        config = _storage(tmp_path).leer()

        assert config.version_esquema == SCHEMA_VERSION
        assert config.tema == "claro"
        assert config.metodo_comparacion_defecto == MetodoComparacion.TAMAÑO_FECHA
        assert config.ultimas_rutas == {"origen": None, "destino": None}
        assert config.perfiles == []
        assert config.reglas_exclusion == []
        assert config.umbral_eliminaciones == 10
        assert config.timeout_por_archivo == 30
        assert config.limite_historial == 50

    def test_defecto_persiste_en_disco(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        congig1 = storage.leer()
        config2 = storage.leer()

        assert congig1.tema == config2.tema

    def test_lee_archivo_existente(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        original = _config_personalizada()
        storage.escribir(original)

        leida = storage.leer()
        assert leida.tema == "oscuro"
        assert leida.metodo_comparacion_defecto == MetodoComparacion.HASH
        assert leida.umbral_eliminaciones == 5
        assert leida.limite_historial == 100

    def test_json_corrupto_lanza_excepcion(self, tmp_path: Path) -> None:
        settings = tmp_path / "settings.json"
        settings.write_text("{no es json válido", encoding="utf-8")

        with pytest.raises(json.JSONDecodeError):
            _storage(tmp_path).leer()

    def test_json_incompleto_lanza_excepcion(self, tmp_path: Path) -> None:
        settings = tmp_path / "settings.json"
        settings.write_text('{"version_esquema": 1}', encoding="utf-8")

        with pytest.raises(KeyError):
            _storage(tmp_path).leer()


# ── TestConfigStorageEscribir ─────────────────────────────────────────────────


class TestConfigStorageEscribir:
    def test_crea_archivo(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        storage.escribir(_config_personalizada())
        assert (tmp_path / "settings.json").exists()

    def test_archivo_es_json_valido(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        storage.escribir(_config_personalizada())
        texto = (tmp_path / "settings.json").read_text(encoding="utf-8")
        datos = json.loads(texto)
        assert isinstance(datos, dict)

    def test_crea_directorio_padre(self, tmp_path: Path) -> None:
        nested = tmp_path / "subdir" / "data"
        storage = ConfigStorage(nested)
        storage.escribir(_config_personalizada())
        assert (nested / "settings.json").exists()

    def test_sobrescribe_archivo_existente(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        config1 = _config_personalizada()
        storage.escribir(config1)

        config2 = ConfiguracionApp(
            version_esquema=SCHEMA_VERSION,
            tema="claro",
            metodo_comparacion_defecto=MetodoComparacion.TAMAÑO_FECHA,
            ultimas_rutas={"origen": None, "destino": None},
            perfiles=[],
            reglas_exclusion=[],
            restricciones_ruta={"origen_permitido": [], "destino_permitido": []},
            umbral_eliminaciones=20,
            timeout_por_archivo=10,
            limite_historial=25,
        )
        storage.escribir(config2)

        leida = storage.leer()
        assert leida.tema == "claro"
        assert leida.umbral_eliminaciones == 20


# ── TestConfigStorageRoundTrip ────────────────────────────────────────────────


class TestConfigStorageRoundTrip:
    def test_round_trip_configuracion(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        original = _config_personalizada()
        storage.escribir(original)
        leida = storage.leer()

        assert leida.version_esquema == original.version_esquema
        assert leida.tema == original.tema
        assert leida.metodo_comparacion_defecto == original.metodo_comparacion_defecto
        assert leida.ultimas_rutas == original.ultimas_rutas
        assert leida.umbral_eliminaciones == original.umbral_eliminaciones
        assert leida.timeout_por_archivo == original.timeout_por_archivo
        assert leida.limite_historial == original.limite_historial

    def test_round_trip_ultimas_rutas_none(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        config = storage.leer()  # crea defecto
        config.ultimas_rutas["origen"] = "C:/documentos"
        storage.escribir(config)

        leida = storage.leer()
        assert leida.ultimas_rutas["origen"] == "C:/documentos"
        assert leida.ultimas_rutas["destino"] is None

    def test_ruta_property(self, tmp_path: Path) -> None:
        storage = _storage(tmp_path)
        assert storage.ruta == tmp_path / "settings.json"
