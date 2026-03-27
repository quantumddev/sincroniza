/**
 * FilaRegla — fila de una regla de exclusión con controles de activar/eliminar.
 */
import type { Regla, TipoRegla } from '@/lib/tipos'

const ETIQUETAS_TIPO: Record<TipoRegla, string> = {
  ARCHIVO: 'Archivo',
  CARPETA: 'Carpeta',
  AMBOS: 'Ambos',
}

const COLORES_TIPO: Record<TipoRegla, string> = {
  ARCHIVO: 'bg-sky-100 text-sky-700 dark:bg-sky-900/40 dark:text-sky-300',
  CARPETA: 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300',
  AMBOS: 'bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300',
}

interface FilaReglaProps {
  regla: Regla
  onToggle: (regla: Regla) => void
  onEliminar: (regla: Regla) => void
}

export function FilaRegla({ regla, onToggle, onEliminar }: FilaReglaProps) {
  const esUsuario = regla.origen === 'USUARIO'

  return (
    <div className={[
      'flex items-center gap-2 px-3 py-2 rounded-md border transition-colors',
      regla.activa
        ? 'bg-white border-gray-200 dark:bg-gray-800 dark:border-gray-700'
        : 'bg-gray-50 border-gray-200 opacity-60 dark:bg-gray-800/50 dark:border-gray-700',
    ].join(' ')}>
      {/* Toggle activa */}
      <button
        onClick={() => onToggle(regla)}
        className={[
          'relative inline-flex h-5 w-9 items-center rounded-full transition-colors shrink-0',
          regla.activa ? 'bg-blue-500' : 'bg-gray-300 dark:bg-gray-600',
        ].join(' ')}
        title={regla.activa ? 'Desactivar regla' : 'Activar regla'}
      >
        <span className={[
          'inline-block h-3.5 w-3.5 transform rounded-full bg-white shadow transition-transform',
          regla.activa ? 'translate-x-4.5' : 'translate-x-0.5',
        ].join(' ')} />
      </button>

      {/* Patrón */}
      <span className="flex-1 font-mono text-sm text-gray-800 dark:text-gray-200 truncate" title={regla.patron}>
        {regla.patron}
      </span>

      {/* Tipo */}
      <span className={`text-xs px-1.5 py-0.5 rounded font-medium shrink-0 ${COLORES_TIPO[regla.tipo]}`}>
        {ETIQUETAS_TIPO[regla.tipo]}
      </span>

      {/* Origen */}
      <span className={[
        'text-xs px-1.5 py-0.5 rounded font-medium shrink-0',
        esUsuario
          ? 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300'
          : 'bg-gray-100 text-gray-500 dark:bg-gray-700 dark:text-gray-400',
      ].join(' ')}>
        {esUsuario ? 'Usuario' : 'Sistema'}
      </span>

      {/* Eliminar (sólo USUARIO) */}
      {esUsuario && (
        <button
          onClick={() => onEliminar(regla)}
          className="p-1 rounded text-gray-400 hover:text-red-500 dark:hover:text-red-400 transition-colors shrink-0"
          title="Eliminar regla"
        >
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}
    </div>
  )
}
