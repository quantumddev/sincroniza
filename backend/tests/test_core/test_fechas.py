"""
Tests de fechas.py — timestamps ISO 8601 y mtime del filesystem.
"""

import os
import time
from datetime import datetime, timezone

import pytest

from app.core.fechas import (
    iso_a_timestamp,
    obtener_mtime,
    timestamp_a_iso,
    timestamp_ahora,
)

# ── obtener_mtime ─────────────────────────────────────────────────────────────

class TestObtenerMtime:
    def test_devuelve_float(self, tmp_path):
        archivo = tmp_path / "test.txt"
        archivo.write_bytes(b"x")
        mtime = obtener_mtime(str(archivo))
        assert isinstance(mtime, float)
        assert mtime > 0

    def test_archivo_reciente(self, tmp_path):
        archivo = tmp_path / "reciente.txt"
        antes = time.time()
        archivo.write_bytes(b"contenido")
        despues = time.time()
        mtime = obtener_mtime(str(archivo))
        # Tolerancia de 100 ms para diferencias entre relojes del SO
        tolerancia = 0.1
        assert antes - tolerancia <= mtime <= despues + tolerancia

    def test_directorio_existente(self, tmp_path):
        mtime = obtener_mtime(str(tmp_path))
        assert isinstance(mtime, float)
        assert mtime > 0

    def test_archivo_no_existe(self, tmp_path):
        with pytest.raises(OSError):
            obtener_mtime(str(tmp_path / "no_existe.txt"))

    def test_detecta_modificacion(self, tmp_path):
        archivo = tmp_path / "mod.txt"
        archivo.write_bytes(b"v1")
        mtime_antes = obtener_mtime(str(archivo))

        # Esperar un ciclo de tick mínimo de mtime en Windows (resolución ~ 100 ns)
        time.sleep(0.05)
        archivo.write_bytes(b"v2")
        mtime_despues = obtener_mtime(str(archivo))

        assert mtime_despues >= mtime_antes


# ── timestamp_ahora ───────────────────────────────────────────────────────────

class TestTimestampAhora:
    def test_formato_iso_8601(self):
        ts = timestamp_ahora()
        # Debe poder parsearse sin excepciones
        dt = datetime.fromisoformat(ts)
        assert dt.tzinfo is not None

    def test_zona_utc(self):
        ts = timestamp_ahora()
        dt = datetime.fromisoformat(ts)
        assert dt.utcoffset().total_seconds() == 0

    def test_es_reciente(self):
        antes = datetime.now(tz=timezone.utc)
        ts = timestamp_ahora()
        despues = datetime.now(tz=timezone.utc)
        dt = datetime.fromisoformat(ts)
        assert antes <= dt <= despues


# ── timestamp_a_iso ───────────────────────────────────────────────────────────

class TestTimestampAIso:
    def test_conocido(self):
        # 2026-03-27T00:00:00 UTC  →  timestamp POSIX
        dt_ref = datetime(2026, 3, 27, 0, 0, 0, tzinfo=timezone.utc)
        ts_posix = dt_ref.timestamp()
        iso = timestamp_a_iso(ts_posix)
        dt_parsed = datetime.fromisoformat(iso)
        assert dt_parsed == dt_ref

    def test_incluye_zona_horaria(self):
        iso = timestamp_a_iso(0.0)  # Época Unix
        dt = datetime.fromisoformat(iso)
        assert dt.tzinfo is not None

    def test_round_trip_con_iso_a_timestamp(self):
        ts_original = 1743076800.0
        iso = timestamp_a_iso(ts_original)
        ts_recuperado = iso_a_timestamp(iso)
        assert abs(ts_recuperado - ts_original) < 1e-3


# ── iso_a_timestamp ───────────────────────────────────────────────────────────

class TestIsoATimestamp:
    def test_con_zona_horaria(self):
        iso = "2026-03-27T00:00:00+00:00"
        ts = iso_a_timestamp(iso)
        dt_ref = datetime(2026, 3, 27, tzinfo=timezone.utc)
        assert abs(ts - dt_ref.timestamp()) < 1e-3

    def test_sin_zona_horaria_asume_utc(self):
        iso_sin_tz = "2026-03-27T00:00:00"
        iso_con_utc = "2026-03-27T00:00:00+00:00"
        assert abs(iso_a_timestamp(iso_sin_tz) - iso_a_timestamp(iso_con_utc)) < 1e-3

    def test_formato_invalido(self):
        with pytest.raises(ValueError):
            iso_a_timestamp("no-es-una-fecha")
