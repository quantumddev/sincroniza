"""
Tests de glob_matcher.py — evaluación de patrones glob sobre rutas relativas.
"""

import pytest

from app.core.glob_matcher import evaluar_regla, evaluar_reglas
from app.models.enums import OrigenRegla, TipoRegla
from app.models.regla import Regla


def _regla(patron: str, tipo: TipoRegla, activa: bool = True) -> Regla:
    return Regla(
        id="test-id",
        patron=patron,
        tipo=tipo,
        activa=activa,
        origen=OrigenRegla.SISTEMA,
    )


# ── evaluar_regla: patrones sin separador (coinciden en cualquier nivel) ─────

class TestEvaluarReglaSinSeparador:
    def test_extension_en_raiz(self):
        assert evaluar_regla("*.tmp", "archivo.tmp", False)

    def test_extension_en_subdirectorio(self):
        assert evaluar_regla("*.tmp", "deep/path/archivo.tmp", False)

    def test_extension_no_coincide(self):
        assert not evaluar_regla("*.tmp", "archivo.txt", False)

    def test_nombre_exacto(self):
        assert evaluar_regla(".DS_Store", ".DS_Store", False)

    def test_nombre_exacto_en_subdir(self):
        assert evaluar_regla(".DS_Store", "src/assets/.DS_Store", False)

    def test_comodin_simple(self):
        assert evaluar_regla("Thumbs.*", "Thumbs.db", False)

    def test_comodin_no_sobra(self):
        assert not evaluar_regla("*.py", "lib/util.pyx", False)


# ── evaluar_regla: patrones con separador (directorio raíz o profundo) ───────

class TestEvaluarReglaConSeparador:
    def test_directorio_con_doble_glob(self):
        assert evaluar_regla("node_modules/**", "node_modules/pkg/index.js", True)

    def test_directorio_raiz_excluido(self):
        """El directorio raíz del patrón también debe quedar excluido."""
        assert evaluar_regla("node_modules/**", "node_modules", True)

    def test_directorio_en_subdir(self):
        """Patrón con / es efectivo en cualquier nivel gracias al match por la derecha."""
        assert evaluar_regla("node_modules/**", "src/node_modules/lodash/a.js", True)

    def test_patron_git(self):
        assert evaluar_regla(".git/**", ".git/config", False)

    def test_patron_git_directorio(self):
        assert evaluar_regla(".git/**", ".git", True)

    def test_patron_pycache(self):
        assert evaluar_regla("__pycache__/**", "app/core/__pycache__/hashing.cpython-314.pyc", False)

    def test_patron_dist(self):
        assert evaluar_regla("dist/**", "dist/index.html", False)

    def test_no_coincide_otro_directorio(self):
        assert not evaluar_regla("node_modules/**", "src/app/index.js", False)


# ── evaluar_regla: patrones con doble glob inicial (**/) ────────────────────

class TestEvaluarReglaDobleGlob:
    def test_doble_glob_en_cualquier_nivel(self):
        assert evaluar_regla("**/.env", ".env", False)
        assert evaluar_regla("**/.env", "deep/nested/.env", False)

    def test_doble_glob_cero_componentes(self):
        assert evaluar_regla("**/__pycache__/**", "__pycache__/mod.pyc", False)


# ── evaluar_regla: entradas inválidas ────────────────────────────────────────

class TestEvaluarReglaInvalida:
    def test_ruta_vacia(self):
        assert not evaluar_regla("*.tmp", "", False)

    def test_patron_vacio(self):
        assert not evaluar_regla("", "archivo.tmp", False)


# ── evaluar_reglas: filtrado por tipo de elemento ────────────────────────────

class TestEvaluarReglasFiltroPorTipo:
    def test_regla_carpeta_no_aplica_a_archivo(self):
        reglas = [_regla("node_modules/**", TipoRegla.CARPETA)]
        resultado = evaluar_reglas(reglas, "node_modules/pkg.js", es_carpeta=False)
        assert resultado is None

    def test_regla_carpeta_aplica_a_directorio(self):
        reglas = [_regla("node_modules/**", TipoRegla.CARPETA)]
        resultado = evaluar_reglas(reglas, "node_modules/pkg", es_carpeta=True)
        assert resultado is not None

    def test_regla_archivo_no_aplica_a_directorio(self):
        reglas = [_regla("*.tmp", TipoRegla.ARCHIVO)]
        resultado = evaluar_reglas(reglas, "cache.tmp", es_carpeta=True)
        assert resultado is None

    def test_regla_archivo_aplica_a_archivo(self):
        reglas = [_regla("*.tmp", TipoRegla.ARCHIVO)]
        resultado = evaluar_reglas(reglas, "cache.tmp", es_carpeta=False)
        assert resultado is not None

    def test_regla_ambos_aplica_a_archivo(self):
        reglas = [_regla("*.log", TipoRegla.AMBOS)]
        assert evaluar_reglas(reglas, "app.log", es_carpeta=False) is not None

    def test_regla_ambos_aplica_a_carpeta(self):
        reglas = [_regla("logs/**", TipoRegla.AMBOS)]
        assert evaluar_reglas(reglas, "logs/2026", es_carpeta=True) is not None


# ── evaluar_reglas: comportamiento con varias reglas ────────────────────────

class TestEvaluarReglasMultiples:
    def test_retorna_primera_coincidente(self):
        r1 = _regla("*.py",  TipoRegla.ARCHIVO)
        r2 = _regla("*.txt", TipoRegla.ARCHIVO)
        resultado = evaluar_reglas([r1, r2], "main.py", es_carpeta=False)
        assert resultado is r1

    def test_retorna_none_si_ninguna_coincide(self):
        reglas = [_regla("*.py", TipoRegla.ARCHIVO)]
        assert evaluar_reglas(reglas, "imagen.png", es_carpeta=False) is None

    def test_salta_reglas_inactivas(self):
        r_inactiva = _regla("*.py", TipoRegla.ARCHIVO, activa=False)
        r_activa   = _regla("*.py", TipoRegla.ARCHIVO, activa=True)
        # Solo la segunda está activa
        resultado = evaluar_reglas([r_inactiva, r_activa], "main.py", es_carpeta=False)
        assert resultado is r_activa

    def test_lista_vacia_retorna_none(self):
        assert evaluar_reglas([], "main.py", es_carpeta=False) is None

    def test_regla_inactiva_no_coincide_sola(self):
        reglas = [_regla("*.py", TipoRegla.ARCHIVO, activa=False)]
        assert evaluar_reglas(reglas, "main.py", es_carpeta=False) is None
