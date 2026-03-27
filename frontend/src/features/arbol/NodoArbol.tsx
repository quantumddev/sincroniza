/**
 * NodoArbol — fila individual del árbol de diferencias.
 */
import type { NodoAplanado } from '@/lib/tipos'
import { formatearTamano } from '@/lib/formato'
import { useAppStore } from '@/state/useAppStore'
import { IndicadorEstado } from './IndicadorEstado'

interface NodoArbolProps {
  nodo: NodoAplanado
  style: React.CSSProperties
}

export function NodoArbol({ nodo, style }: NodoArbolProps) {
  const { nodosExpandidos, toggleNodoExpandido } = useAppStore()
  const expandido = nodosExpandidos.has(nodo.ruta_relativa)

  const handleToggle = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (nodo.tipo === 'CARPETA') toggleNodoExpandido(nodo.ruta_relativa)
  }

  const nombre = nodo.nombre || nodo.ruta_relativa.split('/').pop() || nodo.ruta_relativa

  return (
    <div
      style={{ ...style, paddingLeft: `${nodo.nivel * 16 + 8}px` }}
      className="flex items-center gap-1.5 pr-3 h-7 hover:bg-gray-50 dark:hover:bg-gray-800/50 cursor-default text-sm select-none"
    >
      {/* Toggle expand */}
      <button
        onClick={handleToggle}
        className="w-4 h-4 flex items-center justify-center shrink-0 text-gray-400"
        tabIndex={-1}
      >
        {nodo.tipo === 'CARPETA' && nodo.tieneHijos ? (
          <svg className={`w-3 h-3 transition-transform ${expandido ? 'rotate-90' : ''}`} fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
          </svg>
        ) : null}
      </button>

      {/* Icono */}
      {nodo.tipo === 'CARPETA' ? (
        <svg className="w-4 h-4 shrink-0 text-amber-500" fill="currentColor" viewBox="0 0 20 20">
          <path d="M2 6a2 2 0 012-2h5l2 2h5a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" />
        </svg>
      ) : (
        <svg className="w-4 h-4 shrink-0 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      )}

      {/* Nombre */}
      <span className="flex-1 truncate text-gray-800 dark:text-gray-200" title={nodo.ruta_relativa}>
        {nombre}
      </span>

      {/* Tamaño */}
      {nodo.tipo !== 'CARPETA' && nodo.tamaño != null && nodo.tamaño > 0 && (
        <span className="text-xs text-gray-400 shrink-0">{formatearTamano(nodo.tamaño)}</span>
      )}

      {/* Estado */}
      <IndicadorEstado estado={nodo.estado} />
    </div>
  )
}
