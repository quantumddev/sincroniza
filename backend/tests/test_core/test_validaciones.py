"""
Tests de validaciones.py — funciones de validación de rutas.
"""

from app.core.validaciones import (
    rutas_iguales,
    ruta_anidada,
    validar_restricciones_opcionales,
    validar_ruta_existe,
)


# ── rutas_iguales ────────────────────────────────────────────────────────────

class TestRutasIguales:
    def test_misma_ruta_literal(self):
        assert rutas_iguales("C:\\Users\\jaime", "C:\\Users\\jaime")

    def test_case_insensitive(self):
        assert rutas_iguales("C:\\Users\\Jaime", "C:\\users\\jaime")

    def test_distintas(self):
        assert not rutas_iguales("C:\\Users\\jaime", "C:\\Users\\ana")

    def test_normpath_aplicado(self):
        # Con y sin trailing separator son iguales
        assert rutas_iguales("C:\\Users\\jaime", "C:\\Users\\jaime\\")

    def test_redundancias_equivalentes(self):
        assert rutas_iguales("C:\\a\\b\\..\\b", "C:\\a\\b")

    def test_separadores_mixtos(self):
        assert rutas_iguales("C:/Users/jaime", "C:\\Users\\jaime")


# ── ruta_anidada ─────────────────────────────────────────────────────────────

class TestRutaAnidada:
    def test_hijo_directo(self):
        assert ruta_anidada("C:\\a\\b", "C:\\a")

    def test_hijo_profundo(self):
        assert ruta_anidada("C:\\a\\b\\c\\d", "C:\\a")

    def test_misma_ruta_no_es_hija(self):
        assert not ruta_anidada("C:\\a\\b", "C:\\a\\b")

    def test_falso_positivo_prefijo(self):
        # C:\abc NO debe ser hijo de C:\a
        assert not ruta_anidada("C:\\abc", "C:\\a")

    def test_padre_no_es_hijo(self):
        assert not ruta_anidada("C:\\a", "C:\\a\\b")

    def test_rutas_completamente_distintas(self):
        assert not ruta_anidada("C:\\x\\y", "C:\\a\\b")

    def test_case_insensitive(self):
        assert ruta_anidada("C:\\A\\B\\C", "C:\\a\\b")

    def test_separadores_mixtos(self):
        assert ruta_anidada("C:/a/b/c", "C:\\a")


# ── validar_ruta_existe ──────────────────────────────────────────────────────

class TestValidarRutaExiste:
    def test_ruta_existente(self, tmp_path):
        archivo = tmp_path / "archivo.txt"
        archivo.write_text("contenido")
        assert validar_ruta_existe(str(archivo))

    def test_directorio_existente(self, tmp_path):
        assert validar_ruta_existe(str(tmp_path))

    def test_ruta_inexistente(self, tmp_path):
        assert not validar_ruta_existe(str(tmp_path / "no_existe.txt"))

    def test_ruta_vacia(self):
        assert not validar_ruta_existe("")


# ── validar_restricciones_opcionales ────────────────────────────────────────

class TestValidarRestriccionesOpcionales:
    def test_lista_vacia_permite_todo(self):
        assert validar_restricciones_opcionales("C:\\cualquier\\ruta", [])

    def test_ruta_igual_a_permitida(self):
        assert validar_restricciones_opcionales(
            "C:\\permitido",
            ["C:\\permitido"],
        )

    def test_ruta_anidada_en_permitida(self):
        assert validar_restricciones_opcionales(
            "C:\\permitido\\subcarpeta\\archivo.txt",
            ["C:\\permitido"],
        )

    def test_ruta_fuera_de_lista(self):
        assert not validar_restricciones_opcionales(
            "D:\\otra\\ruta",
            ["C:\\permitido"],
        )

    def test_coincide_con_al_menos_una(self):
        assert validar_restricciones_opcionales(
            "C:\\zona2\\archivo.txt",
            ["C:\\zona1", "C:\\zona2"],
        )

    def test_case_insensitive(self):
        assert validar_restricciones_opcionales(
            "C:\\PERMITIDO\\archivo.txt",
            ["C:\\permitido"],
        )

    def test_falso_positivo_prefijo(self):
        # C:\permitidoextra no está dentro de C:\permitido
        assert not validar_restricciones_opcionales(
            "C:\\permitidoextra\\archivo.txt",
            ["C:\\permitido"],
        )
