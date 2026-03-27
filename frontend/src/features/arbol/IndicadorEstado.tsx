/**
 * IndicadorEstado — badge de color para un EstadoNodo.
 */
import type { EstadoNodo } from '@/lib/tipos'
import { ETIQUETAS_ESTADO } from '@/lib/formato'

const COLORES: Record<EstadoNodo, string> = {
  NUEVO: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300',
  MODIFICADO: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
  ELIMINADO: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
  IDENTICO: 'bg-gray-100 text-gray-500 dark:bg-gray-700 dark:text-gray-400',
  EXCLUIDO: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300',
  ERROR: 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300',
  OMITIDO: 'bg-gray-100 text-gray-400 dark:bg-gray-700 dark:text-gray-500',
  CONFLICTO_NUBE: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300',
}

interface IndicadorEstadoProps {
  estado: EstadoNodo
}

export function IndicadorEstado({ estado }: IndicadorEstadoProps) {
  return (
    <span className={`text-xs px-1.5 py-0.5 rounded font-medium shrink-0 ${COLORES[estado]}`}>
      {ETIQUETAS_ESTADO[estado]}
    </span>
  )
}
