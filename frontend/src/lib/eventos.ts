/**
 * Receptor de eventos push del backend → frontend.
 *
 * El backend invoca `window.evaluate_js("window.__sincroniza_evento('<json>')")`.
 * Este módulo registra el callback global y enruta los eventos a los stores
 * correspondientes.
 *
 * Ref: §03_arquitectura_frontend.md — «Eventos push»
 */

import type { EventoLog, PlanSincronizacion } from '@/lib/tipos'

// Los stores se importan de forma lazy para evitar dependencias circulares
// en el momento de inicialización.
let _logAgregar: ((e: EventoLog) => void) | null = null
let _appSetEstado: ((tipo: string, datos: unknown) => void) | null = null

/**
 * Inicializa el receptor de eventos push.
 * Debe llamarse una única vez al arrancar la app.
 */
export function inicializarEventos(
  logAgregar: (evento: EventoLog) => void,
  appSetEstado: (tipo: string, datos: unknown) => void,
): void {
  _logAgregar = logAgregar
  _appSetEstado = appSetEstado

  window.__sincroniza_evento = (eventoJson: string) => {
    let evento: EventoLog
    try {
      evento = JSON.parse(eventoJson) as EventoLog
    } catch {
      console.error('[eventos] JSON inválido recibido:', eventoJson)
      return
    }

    // Acumular en el log siempre
    _logAgregar?.(evento)

    // Eventos especiales que actualizan el store principal
    _appSetEstado?.(evento.tipo, evento.datos)
  }
}

// ── Tipos de evento reconocidos ───────────────────────────────────────────────

export const EVENTO_ANALISIS_COMPLETADO = 'analisis_completado'
export const EVENTO_ANALISIS_INICIADO   = 'analisis_iniciado'
export const EVENTO_ANALISIS_ERROR      = 'analisis_error'
export const EVENTO_SYNC_INICIADA       = 'sync_iniciada'
export const EVENTO_SYNC_COMPLETADA     = 'sync_completada'
export const EVENTO_SYNC_CANCELADA      = 'sync_cancelada'
export const EVENTO_SYNC_ERROR          = 'sync_error'
export const EVENTO_PROGRESO_ANALISIS   = 'progreso_analisis'
export const EVENTO_PROGRESO_SYNC       = 'progreso_sync'

// ── Helper: extraer el plan desde el evento analisis_completado ───────────────

export function extraerPlanDelEvento(datos: unknown): PlanSincronizacion | null {
  if (!datos || typeof datos !== 'object') return null
  return datos as PlanSincronizacion
}
