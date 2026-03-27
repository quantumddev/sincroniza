"""
Tests de serialización/deserialización de EntradaFilesystem y NodoArbol.
"""

import pytest

from app.models.enums import EstadoNodo, TipoElemento
from app.models.nodo_arbol import EntradaFilesystem, NodoArbol


@pytest.fixture
def entrada_archivo() -> EntradaFilesystem:
    return EntradaFilesystem(
        ruta_relativa="docs/readme.md",
        tipo=TipoElemento.ARCHIVO,
        tamaño=1024,
        mtime=1743076800.0,
        es_oculto=False,
        es_symlink=False,
    )


@pytest.fixture
def nodo_hoja() -> NodoArbol:
    return NodoArbol(
        nombre="readme.md",
        ruta_relativa="docs/readme.md",
        tipo=TipoElemento.ARCHIVO,
        estado=EstadoNodo.NUEVO,
        tamaño=1024,
        tamaño_destino=None,
        motivo=None,
        hijos=[],
    )


@pytest.fixture
def nodo_carpeta_con_hijos(nodo_hoja) -> NodoArbol:
    return NodoArbol(
        nombre="docs",
        ruta_relativa="docs",
        tipo=TipoElemento.CARPETA,
        estado=EstadoNodo.NUEVO,
        tamaño=0,
        tamaño_destino=None,
        motivo=None,
        hijos=[nodo_hoja],
    )


# ── EntradaFilesystem ────────────────────────────────────────────────────────

def test_entrada_filesystem_to_dict(entrada_archivo):
    d = entrada_archivo.to_dict()
    assert d["ruta_relativa"] == "docs/readme.md"
    assert d["tipo"] == "ARCHIVO"
    assert d["tamaño"] == 1024
    assert d["es_oculto"] is False


def test_entrada_filesystem_round_trip(entrada_archivo):
    reconstruida = EntradaFilesystem.from_dict(entrada_archivo.to_dict())
    assert reconstruida == entrada_archivo


def test_entrada_filesystem_es_frozen():
    e = EntradaFilesystem(
        ruta_relativa="x",
        tipo=TipoElemento.CARPETA,
        tamaño=0,
        mtime=0.0,
        es_oculto=False,
        es_symlink=False,
    )
    with pytest.raises(Exception):
        e.tamaño = 1  # type: ignore[misc]


# ── NodoArbol ────────────────────────────────────────────────────────────────

def test_nodo_hoja_to_dict(nodo_hoja):
    d = nodo_hoja.to_dict()
    assert d["nombre"] == "readme.md"
    assert d["estado"] == "NUEVO"
    assert d["tamaño_destino"] is None
    assert d["hijos"] == []


def test_nodo_hoja_round_trip(nodo_hoja):
    reconstruido = NodoArbol.from_dict(nodo_hoja.to_dict())
    assert reconstruido.nombre == nodo_hoja.nombre
    assert reconstruido.estado == EstadoNodo.NUEVO
    assert reconstruido.hijos == []


def test_nodo_carpeta_serializa_hijos(nodo_carpeta_con_hijos):
    d = nodo_carpeta_con_hijos.to_dict()
    assert len(d["hijos"]) == 1
    assert d["hijos"][0]["nombre"] == "readme.md"


def test_nodo_carpeta_round_trip(nodo_carpeta_con_hijos):
    reconstruido = NodoArbol.from_dict(nodo_carpeta_con_hijos.to_dict())
    assert len(reconstruido.hijos) == 1
    assert reconstruido.hijos[0].estado == EstadoNodo.NUEVO


def test_nodo_excluido_con_motivo():
    nodo = NodoArbol(
        nombre=".git",
        ruta_relativa=".git",
        tipo=TipoElemento.CARPETA,
        estado=EstadoNodo.EXCLUIDO,
        tamaño=0,
        tamaño_destino=None,
        motivo="Coincide con regla: .git/**",
        hijos=[],
    )
    d = nodo.to_dict()
    assert d["motivo"] == "Coincide con regla: .git/**"
    reconstruido = NodoArbol.from_dict(d)
    assert reconstruido.motivo == nodo.motivo
