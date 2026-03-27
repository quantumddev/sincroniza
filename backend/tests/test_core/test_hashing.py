"""
Tests de hashing.py — cálculo de hash SHA-256 de archivos.
"""

import hashlib
import os

import pytest

from app.core.hashing import TAMAÑO_BLOQUE_DEFECTO, calcular_hash_archivo


# ── Utilidad de referencia ───────────────────────────────────────────────────

def _sha256_de_bytes(datos: bytes) -> str:
    return hashlib.sha256(datos).hexdigest()


# ── calcular_hash_archivo ────────────────────────────────────────────────────

class TestCalcularHashArchivo:
    def test_archivo_vacio(self, tmp_path):
        archivo = tmp_path / "vacio.bin"
        archivo.write_bytes(b"")
        resultado = calcular_hash_archivo(str(archivo))
        assert resultado == _sha256_de_bytes(b"")

    def test_contenido_conocido(self, tmp_path):
        contenido = b"Sincroniza V1 test"
        archivo = tmp_path / "test.txt"
        archivo.write_bytes(contenido)
        assert calcular_hash_archivo(str(archivo)) == _sha256_de_bytes(contenido)

    def test_hash_es_hexadecimal_64_caracteres(self, tmp_path):
        archivo = tmp_path / "hex.txt"
        archivo.write_bytes(b"abc")
        h = calcular_hash_archivo(str(archivo))
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_archivos_distintos_hashes_distintos(self, tmp_path):
        a = tmp_path / "a.bin"
        b = tmp_path / "b.bin"
        a.write_bytes(b"contenido_a")
        b.write_bytes(b"contenido_b")
        assert calcular_hash_archivo(str(a)) != calcular_hash_archivo(str(b))

    def test_archivos_identicos_mismo_hash(self, tmp_path):
        a = tmp_path / "a.bin"
        b = tmp_path / "b.bin"
        datos = b"mismo contenido"
        a.write_bytes(datos)
        b.write_bytes(datos)
        assert calcular_hash_archivo(str(a)) == calcular_hash_archivo(str(b))

    def test_lectura_multi_bloque(self, tmp_path):
        """Archivo más grande que el bloque por defecto → mismo hash que hashlib."""
        datos = os.urandom(TAMAÑO_BLOQUE_DEFECTO * 3 + 1234)
        archivo = tmp_path / "grande.bin"
        archivo.write_bytes(datos)
        assert calcular_hash_archivo(str(archivo)) == _sha256_de_bytes(datos)

    def test_bloque_personalizado(self, tmp_path):
        datos = b"bloque pequeno" * 100
        archivo = tmp_path / "custom.bin"
        archivo.write_bytes(datos)
        hash_defecto = calcular_hash_archivo(str(archivo))
        hash_bloque_1 = calcular_hash_archivo(str(archivo), tamaño_bloque=1)
        assert hash_defecto == hash_bloque_1

    def test_archivo_no_existe(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            calcular_hash_archivo(str(tmp_path / "no_existe.bin"))

    def test_tamaño_bloque_invalido(self, tmp_path):
        archivo = tmp_path / "test.bin"
        archivo.write_bytes(b"x")
        with pytest.raises(ValueError):
            calcular_hash_archivo(str(archivo), tamaño_bloque=0)
        with pytest.raises(ValueError):
            calcular_hash_archivo(str(archivo), tamaño_bloque=-1)
