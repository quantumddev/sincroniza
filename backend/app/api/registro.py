"""
Registro de métodos JSON-RPC — conecta el Dispatcher con los servicios.

Registra todos los manejadores de la API en el dispatcher inyectando los
servicios necesarios mediante closures. Las operaciones largas
(``analisis.ejecutar``, ``sync.ejecutar``) se ejecutan en hilos worker.

Namespaces registrados:
  config.*      — Configuración global
  perfil.*      — CRUD de perfiles
  reglas.*      — CRUD de reglas de exclusión
  validacion.*  — Validación de rutas
  analisis.*    — Análisis de diferencias (hilo worker)
  sync.*        — Ejecución de sincronización (hilo worker)
  historial.*   — Historial de ejecuciones
  sistema.*     — Servicios del sistema operativo

Ref: §04_protocolo_jsonrpc.md — Catálogo de métodos
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Any

from app.api.dispatcher import (
    ERR_INVALID_PARAMS,
    ERR_OP_IN_PROGRESS,
    ERR_PERFIL_NF,
    ERR_STALE_PLAN,
    ERR_HISTORIAL_NF,
    ERR_REGLA_INVALID,
    ERR_VALIDATION,
    Dispatcher,
    ErrorAPI,
)
from app.models.configuracion import ConfiguracionApp
from app.models.enums import MetodoComparacion, TipoRegla
from app.models.perfil import Perfil
from app.models.plan import PlanSincronizacion
from app.models.regla import Regla
from app.services.comparador import ComparadorServicio
from app.services.historial import HistorialServicio
from app.services.log import LogServicio
from app.services.perfiles import PerfilServicio
from app.services.reglas import ReglasServicio
from app.services.sincronizador import SincronizadorServicio
from app.services.validador import ValidadorServicio
from app.storage.config_storage import ConfigStorage


# ── Contenedor de servicios ───────────────────────────────────────────────────

@dataclass
class Servicios:
    """
    Contenedor inmutable de todos los servicios de la aplicación.

    ``main.py`` construye esta instancia y la pasa a ``registrar_todos()``.
    """
    config_storage: ConfigStorage
    perfil_servicio: PerfilServicio
    reglas_servicio: ReglasServicio
    validador_servicio: ValidadorServicio
    comparador_servicio: ComparadorServicio
    sincronizador_servicio: SincronizadorServicio
    historial_servicio: HistorialServicio
    log_servicio: LogServicio


# ── Registro principal ────────────────────────────────────────────────────────

def registrar_todos(
    dispatcher: Dispatcher,
    servicios: Servicios,
    window: object | None = None,
) -> None:
    """
    Registra todos los métodos de la API en el ``dispatcher``.

    Args:
        dispatcher: Instancia del ``Dispatcher`` donde se registran los métodos.
        servicios:  Contenedor con todos los servicios de la aplicación.
        window:     Ventana pywebview (opcional, usada para ``sistema.*``).
    """
    # ── Estado compartido para operaciones largas ─────────────────────────────
    _planes: dict[str, PlanSincronizacion] = {}
    _cancel_event = threading.Event()
    _worker_lock = threading.Lock()
    _worker_activo: list[bool] = [False]  # lista para mutabilidad en closures

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _hay_worker_activo() -> bool:
        with _worker_lock:
            return _worker_activo[0]

    def _iniciar_worker() -> bool:
        """Marca el worker como activo. Devuelve False si ya hay uno en curso."""
        with _worker_lock:
            if _worker_activo[0]:
                return False
            _worker_activo[0] = True
            _cancel_event.clear()
            return True

    def _finalizar_worker() -> None:
        with _worker_lock:
            _worker_activo[0] = False

    # ── config.* ─────────────────────────────────────────────────────────────

    def config_obtener(params: dict) -> dict:
        return servicios.config_storage.leer().to_dict()

    def config_guardar(params: dict) -> dict:
        config_data = params.get("config")
        if config_data is None:
            raise ErrorAPI(ERR_INVALID_PARAMS, "Falta el parámetro 'config'")
        try:
            config = ConfiguracionApp.from_dict(config_data)
        except (KeyError, ValueError) as exc:
            raise ErrorAPI(ERR_INVALID_PARAMS, f"Configuración inválida: {exc}") from exc
        servicios.config_storage.escribir(config)
        return {"ok": True}

    # ── perfil.* ─────────────────────────────────────────────────────────────

    def perfil_listar(params: dict) -> list:
        return [p.to_dict() for p in servicios.perfil_servicio.listar()]

    def perfil_obtener(params: dict) -> dict:
        perfil_id = params.get("id")
        if not perfil_id:
            raise ErrorAPI(ERR_INVALID_PARAMS, "Falta el parámetro 'id'")
        perfil = servicios.perfil_servicio.obtener(perfil_id)
        if perfil is None:
            raise ErrorAPI(ERR_PERFIL_NF, f"Perfil no encontrado: {perfil_id}")
        return perfil.to_dict()

    def perfil_crear(params: dict) -> dict:
        datos = params.get("perfil")
        if not datos:
            raise ErrorAPI(ERR_INVALID_PARAMS, "Falta el parámetro 'perfil'")
        try:
            metodo_raw = datos.get("metodo_comparacion")
            metodo = MetodoComparacion(metodo_raw) if metodo_raw else None
            perfil = servicios.perfil_servicio.crear(
                nombre=datos["nombre"],
                origen=datos["origen"],
                destino=datos["destino"],
                metodo_comparacion=metodo,
                reglas_exclusion_ids=datos.get("reglas_exclusion_ids"),
                reglas_propias=[Regla.from_dict(r) for r in datos.get("reglas_propias", [])],
                umbral_eliminaciones=datos.get("umbral_eliminaciones"),
                timeout_por_archivo=datos.get("timeout_por_archivo"),
            )
        except KeyError as exc:
            raise ErrorAPI(ERR_INVALID_PARAMS, f"Parámetro requerido ausente: {exc}") from exc
        except ValueError as exc:
            raise ErrorAPI(ERR_INVALID_PARAMS, f"Valor inválido: {exc}") from exc
        return perfil.to_dict()

    def perfil_actualizar(params: dict) -> dict:
        perfil_id = params.get("id")
        cambios = params.get("cambios")
        if not perfil_id:
            raise ErrorAPI(ERR_INVALID_PARAMS, "Falta el parámetro 'id'")
        if cambios is None:
            raise ErrorAPI(ERR_INVALID_PARAMS, "Falta el parámetro 'cambios'")
        try:
            perfil = servicios.perfil_servicio.actualizar(perfil_id, cambios)
        except KeyError:
            raise ErrorAPI(ERR_PERFIL_NF, f"Perfil no encontrado: {perfil_id}")
        return perfil.to_dict()

    def perfil_eliminar(params: dict) -> dict:
        perfil_id = params.get("id")
        if not perfil_id:
            raise ErrorAPI(ERR_INVALID_PARAMS, "Falta el parámetro 'id'")
        servicios.perfil_servicio.eliminar(perfil_id)
        return {"ok": True}

    # ── reglas.* ─────────────────────────────────────────────────────────────

    def reglas_listar(params: dict) -> list:
        return [r.to_dict() for r in servicios.reglas_servicio.listar()]

    def reglas_guardar(params: dict) -> dict:
        reglas_data = params.get("reglas")
        if reglas_data is None:
            raise ErrorAPI(ERR_INVALID_PARAMS, "Falta el parámetro 'reglas'")
        try:
            nuevas_reglas = [Regla.from_dict(r) for r in reglas_data]
        except (KeyError, ValueError) as exc:
            raise ErrorAPI(ERR_REGLA_INVALID, f"Regla inválida: {exc}") from exc
        config = servicios.config_storage.leer()
        config.reglas_exclusion = list(nuevas_reglas)
        servicios.config_storage.escribir(config)
        return {"ok": True}

    # ── validacion.* ─────────────────────────────────────────────────────────

    def validacion_verificar_rutas(params: dict) -> dict:
        origen = params.get("origen")
        destino = params.get("destino")
        if not origen or not destino:
            raise ErrorAPI(ERR_INVALID_PARAMS, "Se requieren los parámetros 'origen' y 'destino'")
        valido, errores = servicios.validador_servicio.validar_rutas(origen, destino)
        return {"valido": valido, "errores": errores}

    # ── analisis.* ───────────────────────────────────────────────────────────

    def analisis_ejecutar(params: dict) -> dict:
        perfil_id = params.get("perfil_id")
        if not perfil_id:
            raise ErrorAPI(ERR_INVALID_PARAMS, "Falta el parámetro 'perfil_id'")

        perfil = servicios.perfil_servicio.obtener(perfil_id)
        if perfil is None:
            raise ErrorAPI(ERR_PERFIL_NF, f"Perfil no encontrado: {perfil_id}")

        if not _iniciar_worker():
            raise ErrorAPI(ERR_OP_IN_PROGRESS, "Ya hay una operación en curso")

        def _worker() -> None:
            try:
                servicios.log_servicio.info("analisis_iniciado", "Análisis iniciado")
                reglas = servicios.reglas_servicio.listar()
                plan = servicios.comparador_servicio.analizar(
                    origen=perfil.origen,
                    destino=perfil.destino,
                    perfil=perfil,
                    reglas=reglas,
                )
                _planes[plan.id] = plan
                servicios.log_servicio.info(
                    "analisis_completado",
                    "Análisis completado",
                    datos=plan.to_dict(),
                )
            except Exception as exc:  # noqa: BLE001
                servicios.log_servicio.error(
                    "analisis_error",
                    f"Error durante el análisis: {exc}",
                )
            finally:
                _finalizar_worker()

        hilo = threading.Thread(target=_worker, daemon=True)
        hilo.start()
        return {"ok": True}

    def analisis_cancelar(params: dict) -> dict:
        _cancel_event.set()
        return {"ok": True}

    # ── sync.* ────────────────────────────────────────────────────────────────

    def sync_ejecutar(params: dict) -> dict:
        plan_id = params.get("plan_id")
        modo_prueba = bool(params.get("modo_prueba", False))

        if not plan_id:
            raise ErrorAPI(ERR_INVALID_PARAMS, "Falta el parámetro 'plan_id'")

        plan = _planes.get(plan_id)
        if plan is None:
            raise ErrorAPI(ERR_STALE_PLAN, f"Plan no encontrado o expirado: {plan_id}")

        if not servicios.validador_servicio.verificar_fingerprint(plan):
            raise ErrorAPI(ERR_STALE_PLAN, "El plan ha quedado desactualizado; ejecute un nuevo análisis")

        if not _iniciar_worker():
            raise ErrorAPI(ERR_OP_IN_PROGRESS, "Ya hay una operación en curso")

        def _worker() -> None:
            try:
                servicios.log_servicio.info("sync_iniciada", "Sincronización iniciada")
                resultado = servicios.sincronizador_servicio.ejecutar(
                    plan=plan,
                    cancel_event=_cancel_event,
                    modo_prueba=modo_prueba,
                )
                # Actualizar última ejecución del perfil
                try:
                    servicios.perfil_servicio.actualizar_ultima_ejecucion(plan.perfil_id)
                except KeyError:
                    pass
                # Persistir en historial
                servicios.historial_servicio.guardar(resultado)
                servicios.log_servicio.info(
                    "sync_completada",
                    "Sincronización completada",
                    datos=resultado.to_dict(),
                )
            except Exception as exc:  # noqa: BLE001
                servicios.log_servicio.error(
                    "sync_error",
                    f"Error durante la sincronización: {exc}",
                )
            finally:
                _finalizar_worker()

        hilo = threading.Thread(target=_worker, daemon=True)
        hilo.start()
        return {"ok": True}

    def sync_cancelar(params: dict) -> dict:
        _cancel_event.set()
        return {"ok": True}

    def sync_reintentar_errores(params: dict) -> dict:
        plan_id = params.get("plan_id")
        rutas = params.get("rutas")

        if not plan_id:
            raise ErrorAPI(ERR_INVALID_PARAMS, "Falta el parámetro 'plan_id'")
        if not isinstance(rutas, list):
            raise ErrorAPI(ERR_INVALID_PARAMS, "El parámetro 'rutas' debe ser una lista")

        plan = _planes.get(plan_id)
        if plan is None:
            raise ErrorAPI(ERR_STALE_PLAN, f"Plan no encontrado o expirado: {plan_id}")

        if not _iniciar_worker():
            raise ErrorAPI(ERR_OP_IN_PROGRESS, "Ya hay una operación en curso")

        # Crear sub-plan solo con las operaciones de las rutas indicadas
        rutas_set = set(rutas)
        ops_reintento = [op for op in plan.operaciones if op.ruta_relativa in rutas_set]

        from app.models.plan import PlanSincronizacion as _Plan
        import uuid as _uuid
        from app.core.fechas import timestamp_ahora as _ts

        sub_plan = _Plan(
            id=str(_uuid.uuid4()),
            perfil_id=plan.perfil_id,
            origen=plan.origen,
            destino=plan.destino,
            metodo_comparacion=plan.metodo_comparacion,
            reglas_activas=plan.reglas_activas,
            arbol=plan.arbol,
            operaciones=ops_reintento,
            resumen=plan.resumen,
            fingerprint=plan.fingerprint,
            mtime_origen=plan.mtime_origen,
            mtime_destino=plan.mtime_destino,
            timestamp=_ts(),
        )

        def _worker() -> None:
            try:
                servicios.log_servicio.info("sync_iniciada", "Reintentando operaciones fallidas")
                resultado = servicios.sincronizador_servicio.ejecutar(
                    plan=sub_plan,
                    cancel_event=_cancel_event,
                    modo_prueba=False,
                )
                servicios.historial_servicio.guardar(resultado)
                servicios.log_servicio.info(
                    "sync_completada",
                    "Reintento completado",
                    datos=resultado.to_dict(),
                )
            except Exception as exc:  # noqa: BLE001
                servicios.log_servicio.error(
                    "sync_error",
                    f"Error durante el reintento: {exc}",
                )
            finally:
                _finalizar_worker()

        hilo = threading.Thread(target=_worker, daemon=True)
        hilo.start()
        return {"ok": True}

    # ── historial.* ───────────────────────────────────────────────────────────

    def historial_listar(params: dict) -> dict:
        pagina = int(params.get("pagina", 1))
        limite = int(params.get("limite", 20))
        resultado = servicios.historial_servicio.listar(pagina=pagina, limite=limite)
        items_serialized = [
            item.to_dict() if hasattr(item, "to_dict") else item
            for item in resultado["items"]
        ]
        return {"items": items_serialized, "total": resultado["total"]}

    def historial_obtener(params: dict) -> dict:
        resultado_id = params.get("id")
        if not resultado_id:
            raise ErrorAPI(ERR_INVALID_PARAMS, "Falta el parámetro 'id'")
        resultado = servicios.historial_servicio.obtener(resultado_id)
        if resultado is None:
            raise ErrorAPI(ERR_HISTORIAL_NF, f"Historial no encontrado: {resultado_id}")
        return resultado.to_dict()

    def historial_eliminar(params: dict) -> dict:
        resultado_id = params.get("id")
        if not resultado_id:
            raise ErrorAPI(ERR_INVALID_PARAMS, "Falta el parámetro 'id'")
        eliminado = servicios.historial_servicio.eliminar(resultado_id)
        if not eliminado:
            raise ErrorAPI(ERR_HISTORIAL_NF, f"Historial no encontrado: {resultado_id}")
        return {"ok": True}

    # ── sistema.* ────────────────────────────────────────────────────────────

    def sistema_seleccionar_directorio(params: dict) -> dict:
        titulo = params.get("titulo", "Seleccionar carpeta")
        ruta_inicial = params.get("ruta_inicial") or ""

        if window is None:
            return {"ruta": None}

        try:
            import webview  # type: ignore[import-untyped]
            resultado = window.create_file_dialog(  # type: ignore[union-attr]
                webview.FOLDER_DIALOG,
                directory=ruta_inicial,
                allow_multiple=False,
            )
            ruta = resultado[0] if resultado else None
            return {"ruta": ruta}
        except Exception:  # noqa: BLE001
            return {"ruta": None}

    # ── Registro en el dispatcher ────────────────────────────────────────────

    dispatcher.registrar("config.obtener", config_obtener)
    dispatcher.registrar("config.guardar", config_guardar)

    dispatcher.registrar("perfil.listar", perfil_listar)
    dispatcher.registrar("perfil.obtener", perfil_obtener)
    dispatcher.registrar("perfil.crear", perfil_crear)
    dispatcher.registrar("perfil.actualizar", perfil_actualizar)
    dispatcher.registrar("perfil.eliminar", perfil_eliminar)

    dispatcher.registrar("reglas.listar", reglas_listar)
    dispatcher.registrar("reglas.guardar", reglas_guardar)

    dispatcher.registrar("validacion.verificar_rutas", validacion_verificar_rutas)

    dispatcher.registrar("analisis.ejecutar", analisis_ejecutar)
    dispatcher.registrar("analisis.cancelar", analisis_cancelar)

    dispatcher.registrar("sync.ejecutar", sync_ejecutar)
    dispatcher.registrar("sync.cancelar", sync_cancelar)
    dispatcher.registrar("sync.reintentar_errores", sync_reintentar_errores)

    dispatcher.registrar("historial.listar", historial_listar)
    dispatcher.registrar("historial.obtener", historial_obtener)
    dispatcher.registrar("historial.eliminar", historial_eliminar)

    dispatcher.registrar("sistema.seleccionar_directorio", sistema_seleccionar_directorio)
