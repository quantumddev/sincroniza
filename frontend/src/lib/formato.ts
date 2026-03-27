/**
 * Helpers de formateo para la UI.
 * Todas las funciones son puras y sin efectos secundarios.
 */

// ── Tamaños en bytes ──────────────────────────────────────────────────────────

/**
 * Formatea un tamaño en bytes a una cadena legible (KB, MB, GB).
 */
export function formatearTamano(bytes: number): string {
  if (bytes < 0) return '0 B'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`
}

// ── Fechas y duraciones ───────────────────────────────────────────────────────

/**
 * Formatea una cadena ISO 8601 a formato legible local (dd/mm/aaaa hh:mm:ss).
 */
export function formatearFecha(iso: string): string {
  if (!iso) return '—'
  try {
    const d = new Date(iso)
    if (isNaN(d.getTime())) return iso
    return d.toLocaleString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    })
  } catch {
    return iso
  }
}

/**
 * Formatea una hora ISO 8601 mostrando solo hh:mm:ss.
 */
export function formatearHora(iso: string): string {
  if (!iso) return '—'
  try {
    const d = new Date(iso)
    if (isNaN(d.getTime())) return iso
    return d.toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    })
  } catch {
    return iso
  }
}

/**
 * Formatea una duración en segundos a cadena legible (ej: "1m 23s", "45s").
 */
export function formatearDuracion(segundos: number): string {
  if (segundos < 0) return '0s'
  const mins = Math.floor(segundos / 60)
  const secs = Math.round(segundos % 60)
  if (mins === 0) return `${secs}s`
  return `${mins}m ${secs}s`
}

// ── Texto de estados ──────────────────────────────────────────────────────────

import type { EstadoNodo, EstadoEjecucion, MetodoComparacion } from '@/lib/tipos'

export const ETIQUETAS_ESTADO: Record<EstadoNodo, string> = {
  NUEVO:          'Nuevo',
  MODIFICADO:     'Modificado',
  ELIMINADO:      'Eliminado',
  IDENTICO:       'Idéntico',
  EXCLUIDO:       'Excluido',
  ERROR:          'Error',
  OMITIDO:        'Omitido',
  CONFLICTO_NUBE: 'Conflicto',
}

export const ETIQUETAS_EJECUCION: Record<EstadoEjecucion, string> = {
  COMPLETADO:              'Completado',
  COMPLETADO_CON_ERRORES:  'Con errores',
  CANCELADO:               'Cancelado',
  FALLIDO:                 'Fallido',
}

export const ETIQUETAS_METODO: Record<MetodoComparacion, string> = {
  TAMAÑO_FECHA: 'Tamaño + Fecha',
  HASH:         'Hash SHA-256',
}

// ── Plurales simples ──────────────────────────────────────────────────────────

/**
 * Devuelve el sustantivo en singular o plural según la cantidad.
 * Ejemplo: pluralizar(1, 'archivo', 'archivos') → 'archivo'
 */
export function pluralizar(n: number, singular: string, plural: string): string {
  return n === 1 ? singular : plural
}
