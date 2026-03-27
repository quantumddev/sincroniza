/**
 * SelectorRuta — campo de texto + botón para elegir directorio vía pywebview.
 */
import { useState } from 'react'
import { llamarRpc } from '@/lib/rpc'

interface SelectorRutaProps {
  valor: string
  onChange: (ruta: string) => void
  placeholder?: string
  label?: string
  titulo?: string
  disabled?: boolean
  id?: string
}

export function SelectorRuta({
  valor,
  onChange,
  placeholder = 'Ruta del directorio…',
  label,
  titulo = 'Seleccionar carpeta',
  disabled = false,
  id,
}: SelectorRutaProps) {
  const [seleccionando, setSeleccionando] = useState(false)

  const seleccionar = async () => {
    if (disabled) return
    setSeleccionando(true)
    try {
      const r = await llamarRpc<{ ruta: string | null }>(
        'sistema.seleccionar_directorio',
        { titulo, ruta_inicial: valor || '' },
      )
      if (r.ruta) onChange(r.ruta)
    } catch {
      // El usuario canceló el diálogo o no hay pywebview
    } finally {
      setSeleccionando(false)
    }
  }

  return (
    <div className="flex flex-col gap-1">
      {label && (
        <label
          htmlFor={id}
          className="text-xs font-medium text-gray-600 dark:text-gray-400"
        >
          {label}
        </label>
      )}
      <div className="flex gap-1.5">
        <input
          id={id}
          type="text"
          value={valor}
          onChange={e => onChange(e.target.value)}
          placeholder={placeholder}
          disabled={disabled}
          spellCheck={false}
          className="flex-1 px-2.5 py-1.5 text-sm rounded-md border
                     border-gray-300 dark:border-gray-600
                     bg-white dark:bg-gray-800
                     text-gray-900 dark:text-gray-100
                     placeholder:text-gray-400 dark:placeholder:text-gray-500
                     focus:outline-none focus:ring-2 focus:ring-blue-500
                     disabled:opacity-50 disabled:cursor-not-allowed
                     font-mono text-xs"
        />
        <button
          type="button"
          onClick={seleccionar}
          disabled={disabled || seleccionando}
          title="Explorar…"
          aria-label="Seleccionar directorio"
          className="px-2.5 py-1.5 rounded-md border border-gray-300 dark:border-gray-600
                     bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600
                     text-gray-600 dark:text-gray-300
                     transition-colors disabled:opacity-50 disabled:cursor-not-allowed
                     focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.8} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round"
              d="M2.25 12.75V12A2.25 2.25 0 0 1 4.5 9.75h15A2.25 2.25 0 0 1 21.75 12v.75m-8.69-6.44-2.12-2.12a1.5 1.5 0 0 0-1.061-.44H4.5A2.25 2.25 0 0 0 2.25 6v8.25m19.5 0A2.25 2.25 0 0 1 19.5 16.5H4.5a2.25 2.25 0 0 1-2.25-2.25V6" />
          </svg>
        </button>
      </div>
    </div>
  )
}
