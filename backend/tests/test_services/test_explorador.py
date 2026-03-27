"""
Tests para ExploradorServicio.

Verifica la exploración recursiva de directorios, detección de ocultos,
symlinks y tolerancia a errores de acceso.
"""

from __future__ import annotations

import os

import pytest

from app.models.enums import TipoElemento
from app.services.explorador import ExploradorServicio


# ── Fixture ───────────────────────────────────────────────────────────────────


@pytest.fixture()
def explorador() -> ExploradorServicio:
    return ExploradorServicio()


# ── Helpers ───────────────────────────────────────────────────────────────────


def _rutas(entradas) -> set[str]:
    return {e.ruta_relativa for e in entradas}


def _por_ruta(entradas, ruta_rel: str):
    for e in entradas:
        if e.ruta_relativa == ruta_rel:
            return e
    return None


# ── TestExplorarBasico ────────────────────────────────────────────────────────


class TestExplorarBasico:
    def test_directorio_vacio(self, explorador: ExploradorServicio, tmp_path) -> None:
        resultado = explorador.explorar(str(tmp_path))
        assert resultado == []

    def test_archivo_simple(
        self, explorador: ExploradorServicio, tmp_path
    ) -> None:
        (tmp_path / "archivo.txt").write_text("hola")
        resultado = explorador.explorar(str(tmp_path))
        assert len(resultado) == 1
        assert resultado[0].ruta_relativa == "archivo.txt"
        assert resultado[0].tipo == TipoElemento.ARCHIVO

    def test_carpeta_vacia(self, explorador: ExploradorServicio, tmp_path) -> None:
        (tmp_path / "subcarpeta").mkdir()
        resultado = explorador.explorar(str(tmp_path))
        assert len(resultado) == 1
        carpeta = resultado[0]
        assert carpeta.tipo == TipoElemento.CARPETA
        assert carpeta.tamaño == 0

    def test_estructura_anidada(
        self, explorador: ExploradorServicio, tmp_path
    ) -> None:
        sub = tmp_path / "subdir"
        sub.mkdir()
        (sub / "deep.txt").write_text("x")
        resultado = explorador.explorar(str(tmp_path))
        rutas = _rutas(resultado)
        assert "subdir" in rutas
        assert "subdir/deep.txt" in rutas

    def test_tamaño_archivo(self, explorador: ExploradorServicio, tmp_path) -> None:
        contenido = b"a" * 1024
        (tmp_path / "big.bin").write_bytes(contenido)
        resultado = explorador.explorar(str(tmp_path))
        entrada = _por_ruta(resultado, "big.bin")
        assert entrada is not None
        assert entrada.tamaño == 1024

    def test_mtime_asignado(self, explorador: ExploradorServicio, tmp_path) -> None:
        (tmp_path / "f.txt").write_text("x")
        resultado = explorador.explorar(str(tmp_path))
        assert resultado[0].mtime > 0


# ── TestArchivosOcultos ───────────────────────────────────────────────────────


class TestArchivosOcultos:
    def test_archivo_punto_es_oculto(
        self, explorador: ExploradorServicio, tmp_path
    ) -> None:
        (tmp_path / ".oculto").write_text("x")
        resultado = explorador.explorar(str(tmp_path))
        entrada = _por_ruta(resultado, ".oculto")
        assert entrada is not None
        assert entrada.es_oculto is True

    def test_archivo_normal_no_oculto(
        self, explorador: ExploradorServicio, tmp_path
    ) -> None:
        (tmp_path / "visible.txt").write_text("x")
        resultado = explorador.explorar(str(tmp_path))
        assert resultado[0].es_oculto is False

    def test_carpeta_oculta(
        self, explorador: ExploradorServicio, tmp_path
    ) -> None:
        (tmp_path / ".git").mkdir()
        resultado = explorador.explorar(str(tmp_path))
        carpeta = _por_ruta(resultado, ".git")
        assert carpeta is not None
        assert carpeta.es_oculto is True


# ── TestSymlinks ──────────────────────────────────────────────────────────────


class TestSymlinks:
    def test_symlink_detectado(
        self, explorador: ExploradorServicio, tmp_path
    ) -> None:
        destino = tmp_path / "real.txt"
        destino.write_text("x")
        enlace = tmp_path / "enlace"
        try:
            enlace.symlink_to(destino)
        except (OSError, NotImplementedError):
            pytest.skip("Creación de symlinks no disponible en este entorno")

        resultado = explorador.explorar(str(tmp_path))
        entrada_enlace = _por_ruta(resultado, "enlace")
        assert entrada_enlace is not None
        assert entrada_enlace.es_symlink is True
        assert entrada_enlace.tipo == TipoElemento.SYMLINK

    def test_symlink_no_se_recursiona(
        self, explorador: ExploradorServicio, tmp_path
    ) -> None:
        sub = tmp_path / "subdir"
        sub.mkdir()
        (sub / "archivo.txt").write_text("x")

        enlace = tmp_path / "enlace_dir"
        try:
            enlace.symlink_to(sub)
        except (OSError, NotImplementedError):
            pytest.skip("Creación de symlinks no disponible en este entorno")

        resultado = explorador.explorar(str(tmp_path))
        # No debe existir "enlace_dir/archivo.txt" (no se recursionó)
        assert _por_ruta(resultado, os.path.join("enlace_dir", "archivo.txt")) is None


# ── TestRutasRelativas ────────────────────────────────────────────────────────


class TestRutasRelativas:
    def test_raiz_no_incluida(
        self, explorador: ExploradorServicio, tmp_path
    ) -> None:
        (tmp_path / "doc.pdf").write_text("x")
        resultado = explorador.explorar(str(tmp_path))
        for e in resultado:
            assert not os.path.isabs(e.ruta_relativa)

    def test_ruta_relativa_correcta_anidada(
        self, explorador: ExploradorServicio, tmp_path
    ) -> None:
        sub = tmp_path / "a" / "b"
        sub.mkdir(parents=True)
        (sub / "c.txt").write_text("x")
        resultado = explorador.explorar(str(tmp_path))
        rutas = _rutas(resultado)
        esperada = "a/b/c.txt"
        assert esperada in rutas


# ── TestMultiplesEntradas ─────────────────────────────────────────────────────


class TestMultiplesEntradas:
    def test_multiples_archivos(
        self, explorador: ExploradorServicio, tmp_path
    ) -> None:
        for i in range(5):
            (tmp_path / f"file{i}.txt").write_text(str(i))
        resultado = explorador.explorar(str(tmp_path))
        assert len(resultado) == 5

    def test_archivos_y_carpetas_mixtos(
        self, explorador: ExploradorServicio, tmp_path
    ) -> None:
        (tmp_path / "arch.txt").write_text("x")
        (tmp_path / "sub").mkdir()
        (tmp_path / "sub" / "inner.txt").write_text("y")
        resultado = explorador.explorar(str(tmp_path))
        tipos = {e.tipo for e in resultado}
        assert TipoElemento.ARCHIVO in tipos
        assert TipoElemento.CARPETA in tipos
        assert len(resultado) == 3  # arch.txt, sub, sub/inner.txt
