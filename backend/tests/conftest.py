"""
Fixtures compartidos para todos los tests del backend.
"""

import pytest


@pytest.fixture
def timestamp_iso() -> str:
    return "2026-03-27T12:00:00+00:00"
