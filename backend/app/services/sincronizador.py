"""
SincronizadorServicio — Motor de ejecución de planes de sincronización.

Ejecuta las operaciones de un ``PlanSincronizacion`` en el orden correcto:
  1. CREAR_CARPETA
  2. COPIAR
  3. REEMPLAZAR
  4. ELIMINAR_ARCHIVO
  5. ELIMINAR_CARPETA

Características:
- Escrituras atómicas: copia a ``.tmp_sincroniza`` y luego ``os.replace()``.
- Cancelación cooperativa mediante ``threading.Event``.
- Control de pending-sync para reanudar sincronizaciones interrumpidas.
- Modo prueba (dry-run) que no modifica el filesystem.

Ref: §11, §12
"""

from __future__ import annotations

import os
import shutil
import threading
import time
import uuid

from app.core.fechas import timestamp_ahora
from app.models.configuracion import PendingSync
from app.models.enums import (
    EstadoEjecucion,
    FaseOperacion,
    TipoOperacion,
)
from app.models.error import ErrorSincronizacion
from app.models.plan import OperacionPlanificada, PlanSincronizacion
from app.models.resultado import ResultadoEjecucion
from app.services.log import LogServicio
from app.storage.pending_storage import PendingSyncStorage

# Sufijo temporal para escrituras atómicas
_SUFIJO_TMP = ".tmp_sincroniza"

# Orden de ejecución de tipos de operación
_ORDEN_OPS = [
    TipoOperacion.CREAR_CARPETA,
    TipoOperacion.COPIAR,
    TipoOperacion.REEMPLAZAR,
    TipoOperacion.ELIMINAR_ARCHIVO,
    TipoOperacion.ELIMINAR_CARPETA,
]


class SincronizadorServicio:
    """
    Ejecuta un ``PlanSincronizacion`` operación por operación.

    Args:
        pending_storage: Storage para registrar el estado de la sincronización
                         en curso (permite recuperación ante interrupciones).
        log_servicio:    Servicio de log para emitir eventos durante la ejecución.
    """

    def __init__(
        self,
        pending_storage: PendingSyncStorage,
        log_servicio: LogServicio,
    ) -> None:
        self._pending = pending_storage
        self._log = log_servicio

    # ── Pública ───────────────────────────────────────────────────────────────

    def ejecutar(
        self,
        plan: PlanSincronizacion,
        cancel_event: threading.Event,
        modo_prueba: bool = False,
    ) -> ResultadoEjecucion:
        """
        Ejecuta el plan y devuelve el resultado.

        Args:
            plan:         ``PlanSincronizacion`` a ejecutar.
            cancel_event: Evento de cancelación cooperativo. Si se señaliza,
                          la ejecución se detiene en la siguiente operación.
            modo_prueba:  Si ``True``, simula las operaciones sin tocar el filesystem.

        Returns:
            ``ResultadoEjecucion`` con el resumen de lo ocurrido.
        """
        timestamp_inicio = timestamp_ahora()
        t_inicio = time.monotonic()

        completadas: list[OperacionPlanificada] = []
        fallidas: list[OperacionPlanificada] = []
        errores: list[ErrorSincronizacion] = []
        cancelado = False

        # Ordenar operaciones según el orden establecido
        ops_ordenadas = sorted(
            plan.operaciones,
            key=lambda op: _ORDEN_OPS.index(op.tipo)
            if op.tipo in _ORDEN_OPS
            else len(_ORDEN_OPS),
        )

        # Guardar pending-sync antes de empezar
        pending = PendingSync(
            plan_id=plan.id,
            perfil_id=plan.perfil_id,
            timestamp_inicio=timestamp_inicio,
            operaciones_completadas=[],
            operaciones_pendientes=[op.ruta_relativa for op in ops_ordenadas],
        )
        self._pending.guardar(pending)

        for op in ops_ordenadas:
            if cancel_event.is_set():
                cancelado = True
                self._log.warning("ejecucion", f"Cancelado antes de {op.tipo.value}: {op.ruta_relativa}")
                break

            exito, error = self._ejecutar_operacion(op, modo_prueba, plan.timeout_por_archivo if hasattr(plan, 'timeout_por_archivo') else 30)
            if exito:
                completadas.append(op)
                pending.operaciones_completadas.append(op.ruta_relativa)
                if op.ruta_relativa in pending.operaciones_pendientes:
                    pending.operaciones_pendientes.remove(op.ruta_relativa)
                self._pending.guardar(pending)
                self._log.info("ejecucion", f"OK: {op.tipo.value} {op.ruta_relativa}")
            else:
                fallidas.append(op)
                if error is not None:
                    errores.append(error)
                self._log.error("ejecucion", f"ERROR: {op.tipo.value} {op.ruta_relativa}")

        duracion_ejecucion = time.monotonic() - t_inicio

        # Determinar estado final
        if cancelado:
            estado = EstadoEjecucion.CANCELADO
        elif fallidas:
            estado = (
                EstadoEjecucion.COMPLETADO_CON_ERRORES
                if completadas
                else EstadoEjecucion.FALLIDO
            )
        else:
            estado = EstadoEjecucion.COMPLETADO

        # Limpiar pending-sync
        self._pending.eliminar()

        timestamp_fin = timestamp_ahora()

        return ResultadoEjecucion(
            id=str(uuid.uuid4()),
            plan_id=plan.id,
            perfil_id=plan.perfil_id,
            origen=plan.origen,
            destino=plan.destino,
            metodo_comparacion=plan.metodo_comparacion,
            reglas_activas=list(plan.reglas_activas),
            estado=estado,
            modo_prueba=modo_prueba,
            resumen=plan.resumen,
            operaciones_completadas=completadas,
            operaciones_fallidas=fallidas,
            errores=errores,
            reintentos=[],
            duracion_analisis=0.0,
            duracion_ejecucion=duracion_ejecucion,
            timestamp_inicio=timestamp_inicio,
            timestamp_fin=timestamp_fin,
            version_esquema=1,
        )

    # ── Ejecución de operación individual ─────────────────────────────────────

    def _ejecutar_operacion(
        self,
        op: OperacionPlanificada,
        modo_prueba: bool,
        timeout: int,
    ) -> tuple[bool, ErrorSincronizacion | None]:
        """
        Ejecuta una sola operación.

        Returns:
            Tupla ``(éxito, error_o_None)``.
        """
        resultado: list[tuple[bool, ErrorSincronizacion | None]] = []
        exc_holder: list[Exception] = []

        def _ejecutar() -> None:
            try:
                if modo_prueba:
                    resultado.append((True, None))
                    return
                if op.tipo == TipoOperacion.CREAR_CARPETA:
                    os.makedirs(op.ruta_destino, exist_ok=True)
                elif op.tipo == TipoOperacion.COPIAR:
                    os.makedirs(os.path.dirname(op.ruta_destino), exist_ok=True)
                    _copiar_atomico(op.ruta_origen, op.ruta_destino)
                elif op.tipo == TipoOperacion.REEMPLAZAR:
                    os.makedirs(os.path.dirname(op.ruta_destino), exist_ok=True)
                    _copiar_atomico(op.ruta_origen, op.ruta_destino)
                elif op.tipo == TipoOperacion.ELIMINAR_ARCHIVO:
                    os.remove(op.ruta_destino)
                elif op.tipo == TipoOperacion.ELIMINAR_CARPETA:
                    shutil.rmtree(op.ruta_destino, ignore_errors=False)
                resultado.append((True, None))
            except Exception as exc:
                exc_holder.append(exc)
                resultado.append((False, None))

        hilo = threading.Thread(target=_ejecutar, daemon=True)
        hilo.start()
        hilo.join(timeout=timeout)

        if hilo.is_alive():
            # Timeout expirado
            error = self._crear_error(
                "TIMEOUT",
                f"Operación {op.tipo.value} superó el timeout de {timeout}s",
                op.ruta_relativa,
            )
            return False, error

        if resultado and resultado[0][0]:
            return True, None

        exc = exc_holder[0] if exc_holder else None
        error = self._crear_error(
            "ERROR_IO",
            str(exc) if exc else "Error desconocido",
            op.ruta_relativa,
        )
        return False, error

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _crear_error(
        self, codigo: str, mensaje: str, ruta: str
    ) -> ErrorSincronizacion:
        return ErrorSincronizacion(
            codigo=codigo,
            mensaje=mensaje,
            ruta=ruta,
            fase=FaseOperacion.EJECUCION,
            recuperable=False,
            timestamp=timestamp_ahora(),
        )


def _copiar_atomico(origen: str, destino: str) -> None:
    """
    Copia ``origen`` a ``destino`` de forma atómica usando un archivo temporal.

    Pasos:
    1. Copiar a ``destino + ".tmp_sincroniza"``.
    2. Renombrar atómicamente al destino final con ``os.replace()``.
    """
    tmp = destino + _SUFIJO_TMP
    try:
        shutil.copy2(origen, tmp)
        os.replace(tmp, destino)
    except Exception:
        # Limpiar temporal si existe
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise
