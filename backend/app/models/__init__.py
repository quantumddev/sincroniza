"""
Paquete models — todos los modelos de datos de Sincroniza.

Importaciones públicas del paquete para uso conveniente:
    from app.models import Regla, Perfil, NodoArbol, ...
"""

from app.models.enums import (
    EstadoEjecucion,
    EstadoNodo,
    FaseOperacion,
    MetodoComparacion,
    NivelLog,
    OrigenRegla,
    TipoElemento,
    TipoOperacion,
    TipoRegla,
)
from app.models.regla import Regla
from app.models.perfil import Perfil
from app.models.nodo_arbol import EntradaFilesystem, NodoArbol
from app.models.plan import OperacionPlanificada, PlanSincronizacion, ResumenPlan
from app.models.error import ErrorSincronizacion
from app.models.resultado import ResultadoEjecucion
from app.models.evento_log import EventoLog
from app.models.configuracion import ConfiguracionApp, PendingSync

__all__ = [
    # Enums
    "EstadoEjecucion",
    "EstadoNodo",
    "FaseOperacion",
    "MetodoComparacion",
    "NivelLog",
    "OrigenRegla",
    "TipoElemento",
    "TipoOperacion",
    "TipoRegla",
    # Modelos
    "ConfiguracionApp",
    "EntradaFilesystem",
    "ErrorSincronizacion",
    "EventoLog",
    "NodoArbol",
    "OperacionPlanificada",
    "PendingSync",
    "Perfil",
    "PlanSincronizacion",
    "Regla",
    "ResumenPlan",
    "ResultadoEjecucion",
]
