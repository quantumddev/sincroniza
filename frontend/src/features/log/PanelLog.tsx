/**
 * PanelLog — panel desplegable con los eventos del log en tiempo real.
 * Autoscroll al final cuando llegan nuevos eventos.
 */
import { useEffect, useRef, useState } from 'react'
import { useLogStore } from '@/state/useLogStore'
import { EntradaLog } from './EntradaLog'

export function PanelLog() {
  const { eventos, limpiar } = useLogStore()
  const [abierto, setAbierto] = useState(false)
  const listaRef = useRef<HTMLDivElement>(null)
  const [autoscroll, setAutoscroll] = useState(true)

  // Autoscroll cuando llegan nuevos eventos
  useEffect(() => {
    if (abierto && autoscroll && listaRef.current) {
      listaRef.current.scrollTop = listaRef.current.scrollHeight
    }
  }, [eventos, abierto, autoscroll])

  const onScroll = () => {
    const el = listaRef.current
    if (!el) return
    const enFondo = el.scrollTop + el.clientHeight >= el.scrollHeight - 20
    setAutoscroll(enFondo)
  }

  const contadorError = eventos.filter(e => e.nivel === 'ERROR').length

  return (
    <div className="flex flex-col border-t border-gray-200 dark:border-gray-700 shrink-0">
      {/* Cabecera */}
      <div
        onClick={() => setAbierto(v => !v)}
        className="flex items-center gap-2 px-3 py-2 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50 select-none"
      >
        <svg
          className={`w-4 h-4 text-gray-400 transition-transform ${abierto ? 'rotate-90' : ''}`}
          fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
        </svg>
        <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
          Registro de actividad
        </span>
        {eventos.length > 0 && (
          <span className="text-xs text-gray-400 dark:text-gray-500 ml-1">
            ({eventos.length})
          </span>
        )}
        {contadorError > 0 && (
          <span className="ml-1 px-1.5 py-0 rounded-full text-xs bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400 font-medium">
            {contadorError} error{contadorError !== 1 ? 'es' : ''}
          </span>
        )}
        {abierto && eventos.length > 0 && (
          <button
            onClick={e => { e.stopPropagation(); limpiar() }}
            className="ml-auto text-xs text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            Limpiar
          </button>
        )}
      </div>

      {/* Lista */}
      {abierto && (
        <div
          ref={listaRef}
          onScroll={onScroll}
          className="max-h-48 overflow-y-auto bg-gray-50 dark:bg-gray-900 py-1"
        >
          {eventos.length === 0 ? (
            <p className="text-xs text-gray-400 px-4 py-2">Sin eventos registrados.</p>
          ) : (
            eventos.map((ev, i) => <EntradaLog key={i} evento={ev} />)
          )}
        </div>
      )}
    </div>
  )
}
