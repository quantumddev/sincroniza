"""
Tests de fingerprint.py — hash determinista de parámetros del plan.
"""

import pytest

from app.core.fingerprint import calcular_fingerprint
from app.models.enums import MetodoComparacion


ORIGEN = "C:\\origen"
DESTINO = "D:\\destino"
REGLAS = ["r-001", "r-002"]
METODO = MetodoComparacion.TAMAÑO_FECHA


class TestCalcularFingerprint:
    def test_resultado_es_hexadecimal_64_caracteres(self):
        fp = calcular_fingerprint(ORIGEN, DESTINO, REGLAS, METODO)
        assert len(fp) == 64
        assert all(c in "0123456789abcdef" for c in fp)

    def test_determinista_mismos_argumentos(self):
        fp1 = calcular_fingerprint(ORIGEN, DESTINO, REGLAS, METODO)
        fp2 = calcular_fingerprint(ORIGEN, DESTINO, REGLAS, METODO)
        assert fp1 == fp2

    def test_sensible_a_origen_distinto(self):
        fp1 = calcular_fingerprint("C:\\origenA", DESTINO, REGLAS, METODO)
        fp2 = calcular_fingerprint("C:\\origenB", DESTINO, REGLAS, METODO)
        assert fp1 != fp2

    def test_sensible_a_destino_distinto(self):
        fp1 = calcular_fingerprint(ORIGEN, "D:\\destinoA", REGLAS, METODO)
        fp2 = calcular_fingerprint(ORIGEN, "D:\\destinoB", REGLAS, METODO)
        assert fp1 != fp2

    def test_sensible_a_metodo_distinto(self):
        fp1 = calcular_fingerprint(ORIGEN, DESTINO, REGLAS, MetodoComparacion.TAMAÑO_FECHA)
        fp2 = calcular_fingerprint(ORIGEN, DESTINO, REGLAS, MetodoComparacion.HASH)
        assert fp1 != fp2

    def test_sensible_a_reglas_distintas(self):
        fp1 = calcular_fingerprint(ORIGEN, DESTINO, ["r-001"], METODO)
        fp2 = calcular_fingerprint(ORIGEN, DESTINO, ["r-002"], METODO)
        assert fp1 != fp2

    def test_independiente_del_orden_de_reglas(self):
        """Las reglas se ordenan internamente: el orden de entrada no importa."""
        fp1 = calcular_fingerprint(ORIGEN, DESTINO, ["r-001", "r-002"], METODO)
        fp2 = calcular_fingerprint(ORIGEN, DESTINO, ["r-002", "r-001"], METODO)
        assert fp1 == fp2

    def test_lista_de_reglas_vacia(self):
        fp = calcular_fingerprint(ORIGEN, DESTINO, [], METODO)
        assert len(fp) == 64

    def test_sensible_a_intercambio_origen_destino(self):
        """origen y destino son posicionales: invertirlos da fingerprint distinto."""
        fp1 = calcular_fingerprint(ORIGEN, DESTINO, REGLAS, METODO)
        fp2 = calcular_fingerprint(DESTINO, ORIGEN, REGLAS, METODO)
        assert fp1 != fp2

    def test_case_insensitive_rutas(self):
        """Las rutas se normalizan con normcase: mayúsculas no cambian el resultado."""
        fp1 = calcular_fingerprint("C:\\ORIGEN", DESTINO, REGLAS, METODO)
        fp2 = calcular_fingerprint("C:\\origen", DESTINO, REGLAS, METODO)
        assert fp1 == fp2
