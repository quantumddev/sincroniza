/**
 * FiltrosArbol — chips para activar/desactivar filtros por EstadoNodo.
 */
import type { EstadoNodo } from '@/lib/tipos'
import { ETIQUETAS_ESTADO } from '@/lib/formato'
import { useAppStore } from '@/state/useAppStore'

const ESTADOS_FILTRO: EstadoNodo[] = [
  'NUEVO', 'MODIFICADO', 'ELIMINADO', 'IDENTICO', 'EXCLUIDO', 'ERROR', 'OMITIDO', 'CONFLICTO_NUBE',
]

const COLOR_ACTIVO: Record<EstadoNodo, string> = {
  NUEVO: 'bg-green-500 text-white border-green-500',
  MODIFICADO: 'bg-blue-500 text-white border-blue-500',
  ELIMINADO: 'bg-red-500 text-white border-red-500',
  IDENTICO: 'bg-gray-500 text-white border-gray-500',
  EXCLUIDO: 'bg-yellow-500 text-white border-yellow-500',
  ERROR: 'bg-orange-500 text-white border-orange-500',
  OMITIDO: 'bg-gray-400 text-white border-gray-400',
  CONFLICTO_NUBE: 'bg-purple-500 text-white border-purple-500',
}

export function FiltrosArbol() {
  const { filtrosArbol, toggleFiltroArbol } = useAppStore()

  return (
    <div className="flex flex-wrap gap-1">
      {ESTADOS_FILTRO.map(estado => {
        const activo = filtrosArbol.includes(estado)
        return (
          <button
            key={estado}
            onClick={() => toggleFiltroArbol(estado)}
            className={[
              'text-xs px-2 py-0.5 rounded-full border font-medium transition-colors',
              activo
                ? COLOR_ACTIVO[estado]
                : 'border-gray-300 text-gray-500 hover:border-gray-400 dark:border-gray-600 dark:text-gray-400 dark:hover:border-gray-500',
            ].join(' ')}
          >
            {ETIQUETAS_ESTADO[estado]}
          </button>
        )
      })}
    </div>
  )
}
