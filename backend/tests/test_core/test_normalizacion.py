"""
Tests de normalizacion.py — normalización de rutas Windows.
"""

import os

import pytest

from app.core.normalizacion import (
    a_ruta_larga,
    normalizar_ruta,
    normalizar_separadores,
    quitar_prefijo_largo,
    ruta_a_relativa,
)


# ── normalizar_ruta ──────────────────────────────────────────────────────────

class TestNormalizarRuta:
    def test_elimina_dobles_separadores(self):
        resultado = normalizar_ruta("C:\\\\Users\\\\jaime")
        assert "\\\\" not in resultado

    def test_elimina_punto_actual(self):
        resultado = normalizar_ruta("C:\\Users\\.\\jaime")
        assert "." not in resultado.split(os.sep)

    def test_resuelve_punto_punto(self):
        resultado = normalizar_ruta("C:\\Users\\jaime\\..\\ana")
        assert "ana" in resultado
        assert ".." not in resultado

    def test_ruta_sin_cambios(self):
        ruta = os.path.join("C:", "Users", "jaime", "docs")
        assert normalizar_ruta(ruta) == os.path.normpath(ruta)

    def test_ruta_relativa(self):
        resultado = normalizar_ruta("a/b/../c")
        assert resultado == os.path.normpath("a/b/../c")

    def test_no_realiza_io(self):
        # La ruta no tiene por qué existir
        resultado = normalizar_ruta("Z:\\ruta\\inexistente\\..\\otra")
        assert "inexistente" not in resultado


# ── normalizar_separadores ───────────────────────────────────────────────────

class TestNormalizarSeparadores:
    def test_convierte_backslash_a_slash(self):
        assert normalizar_separadores("a\\b\\c") == "a/b/c"

    def test_ya_tiene_slash(self):
        assert normalizar_separadores("a/b/c") == "a/b/c"

    def test_mixto(self):
        assert normalizar_separadores("a/b\\c/d\\e") == "a/b/c/d/e"

    def test_cadena_vacia(self):
        assert normalizar_separadores("") == ""

    def test_solo_backslash(self):
        assert normalizar_separadores("\\") == "/"


# ── quitar_prefijo_largo ─────────────────────────────────────────────────────

class TestQuitarPrefijoLargo:
    def test_quita_prefijo_local(self):
        assert quitar_prefijo_largo("\\\\?\\C:\\Users\\jaime") == "C:\\Users\\jaime"

    def test_quita_prefijo_unc(self):
        resultado = quitar_prefijo_largo("\\\\?\\UNC\\server\\share\\file.txt")
        assert resultado == "\\\\server\\share\\file.txt"

    def test_sin_prefijo_no_cambia(self):
        ruta = "C:\\Users\\jaime"
        assert quitar_prefijo_largo(ruta) == ruta

    def test_idempotente_sin_prefijo(self):
        ruta = "\\\\server\\share"
        assert quitar_prefijo_largo(ruta) == ruta


# ── a_ruta_larga ─────────────────────────────────────────────────────────────

class TestARutaLarga:
    def test_anade_prefijo_ruta_local(self):
        resultado = a_ruta_larga("C:\\Users\\jaime\\docs")
        assert resultado.startswith("\\\\?\\")
        assert "C:" in resultado

    def test_anade_prefijo_unc(self):
        resultado = a_ruta_larga("\\\\server\\share\\archivo.txt")
        assert resultado.startswith("\\\\?\\UNC\\")
        assert "server" in resultado

    def test_no_duplica_prefijo(self):
        ruta_ya_larga = "\\\\?\\C:\\Users\\jaime"
        assert a_ruta_larga(ruta_ya_larga) == ruta_ya_larga

    def test_round_trip(self):
        """a_ruta_larga y quitar_prefijo_largo son inversas."""
        ruta_original = "C:\\Users\\jaime\\Documents"
        ruta_larga = a_ruta_larga(ruta_original)
        assert quitar_prefijo_largo(ruta_larga) == os.path.normpath(ruta_original)

    def test_normaliza_redundancias(self):
        resultado = a_ruta_larga("C:\\Users\\jaime\\..\\ana")
        assert ".." not in resultado


# ── ruta_a_relativa ──────────────────────────────────────────────────────────

class TestRutaARelativa:
    def test_ruta_directa(self):
        relativa = ruta_a_relativa("C:\\origen\\carpeta\\archivo.txt", "C:\\origen")
        assert relativa == "carpeta/archivo.txt"

    def test_usa_slash_como_separador(self):
        relativa = ruta_a_relativa(
            "C:\\origen\\a\\b\\c.py",
            "C:\\origen",
        )
        assert "\\" not in relativa
        assert "/" in relativa

    def test_ruta_en_raiz(self):
        relativa = ruta_a_relativa("C:\\origen\\file.txt", "C:\\origen")
        assert relativa == "file.txt"

    def test_error_unidades_distintas(self):
        with pytest.raises(ValueError):
            ruta_a_relativa("D:\\destino\\file.txt", "C:\\origen")
