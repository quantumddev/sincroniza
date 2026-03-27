"""
ConfigStorage — lectura y escritura de ``data/settings.json``.

Gestiona la persistencia de la configuración global de la aplicación.
Si el archivo no existe al leer, se crea automáticamente con valores por
defecto y se persiste en disco.

Ref: §13.2
"""

from __future__ import annotations

import json
from pathlib import Path

from app.models.configuracion import ConfiguracionApp
from app.models.enums import MetodoComparacion

# Nombre del archivo relativo al directorio ``data/``.
SETTINGS_FILE = "settings.json"

# Versión actual del esquema de settings.
SCHEMA_VERSION = 1


def _config_por_defecto() -> ConfiguracionApp:
    """Retorna una ``ConfiguracionApp`` con valores iniciales seguros."""
    return ConfiguracionApp(
        version_esquema=SCHEMA_VERSION,
        tema="claro",
        metodo_comparacion_defecto=MetodoComparacion.TAMAÑO_FECHA,
        ultimas_rutas={"origen": None, "destino": None},
        perfiles=[],
        reglas_exclusion=[],
        restricciones_ruta={"origen_permitido": [], "destino_permitido": []},
        umbral_eliminaciones=10,
        timeout_por_archivo=30,
        limite_historial=50,
    )


class ConfigStorage:
    """
    Lee y escribe la configuración de la aplicación en ``data/settings.json``.

    Args:
        data_dir: Ruta al directorio ``data/`` que contiene ``settings.json``.
    """

    def __init__(self, data_dir: Path) -> None:
        self._path = data_dir / SETTINGS_FILE

    # ── API pública ───────────────────────────────────────────────────────────

    def leer(self) -> ConfiguracionApp:
        """
        Retorna la configuración actual.

        Si el archivo no existe, crea uno con valores por defecto, lo persiste
        y devuelve la instancia creada.

        Raises:
            json.JSONDecodeError: Si el archivo existe pero contiene JSON no válido.
        """
        if not self._path.exists():
            config = _config_por_defecto()
            self.escribir(config)
            return config

        texto = self._path.read_text(encoding="utf-8")
        datos = json.loads(texto)
        return ConfiguracionApp.from_dict(datos)

    def escribir(self, config: ConfiguracionApp) -> None:
        """
        Serializa y persiste la configuración en disco.

        Crea el directorio padre si no existe.
        """
        self._path.parent.mkdir(parents=True, exist_ok=True)
        texto = json.dumps(config.to_dict(), ensure_ascii=False, indent=2)
        self._path.write_text(texto, encoding="utf-8")

    @property
    def ruta(self) -> Path:
        """Ruta absoluta al archivo ``settings.json``."""
        return self._path
