/**
 * FormularioRegla — formulario inline para añadir una nueva regla de exclusión.
 */
import { useState } from 'react'
import type { TipoRegla } from '@/lib/tipos'
import { BotonAccion } from '@/components/BotonAccion'

interface FormularioReglaProps {
  onAgregar: (patron: string, tipo: TipoRegla) => void
}

const TIPOS: TipoRegla[] = ['ARCHIVO', 'CARPETA', 'AMBOS']
const ETIQUETAS: Record<TipoRegla, string> = { ARCHIVO: 'Archivo', CARPETA: 'Carpeta', AMBOS: 'Ambos' }

export function FormularioRegla({ onAgregar }: FormularioReglaProps) {
  const [patron, setPatron] = useState('')
  const [tipo, setTipo] = useState<TipoRegla>('ARCHIVO')
  const [error, setError] = useState('')

  const agregar = () => {
    const p = patron.trim()
    if (!p) { setError('El patrón es obligatorio'); return }
    onAgregar(p, tipo)
    setPatron('')
    setError('')
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') agregar()
  }

  return (
    <div className="flex flex-col gap-2 p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-gray-200 dark:border-gray-700">
      <p className="text-xs font-medium text-gray-600 dark:text-gray-400">Nueva regla</p>
      <div className="flex gap-2">
        <input
          type="text"
          value={patron}
          onChange={e => { setPatron(e.target.value); setError('') }}
          onKeyDown={handleKeyDown}
          placeholder="*.tmp, thumbs.db, .git…"
          className="input-base flex-1"
        />
        <select
          value={tipo}
          onChange={e => setTipo(e.target.value as TipoRegla)}
          className="input-base w-28"
        >
          {TIPOS.map(t => (
            <option key={t} value={t}>{ETIQUETAS[t]}</option>
          ))}
        </select>
        <BotonAccion onClick={agregar}>Añadir</BotonAccion>
      </div>
      {error && <p className="text-xs text-red-600 dark:text-red-400">{error}</p>}
    </div>
  )
}
