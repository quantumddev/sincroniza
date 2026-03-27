/**
 * BusquedaArbol — campo de texto para filtrar el árbol por nombre.
 */
import { useRef } from 'react'
import { useAppStore } from '@/state/useAppStore'

export function BusquedaArbol() {
  const { busquedaArbol, setBusquedaArbol } = useAppStore()
  const inputRef = useRef<HTMLInputElement>(null)

  return (
    <div className="relative">
      <svg
        className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none"
        fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
      >
        <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-4.35-4.35M17 11A6 6 0 115 11a6 6 0 0112 0z" />
      </svg>
      <input
        ref={inputRef}
        type="text"
        value={busquedaArbol}
        onChange={e => setBusquedaArbol(e.target.value)}
        placeholder="Buscar archivo…"
        className="input-base pl-8 pr-8 text-sm h-8"
      />
      {busquedaArbol && (
        <button
          onClick={() => setBusquedaArbol('')}
          className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
        >
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}
    </div>
  )
}
