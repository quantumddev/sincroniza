/**
 * FilaHistorial — fila de un resultado de ejecución para la tabla del historial.
 */
import type { ResumenHistorial } from '@/lib/tipos'
import { formatearFecha, formatearDuracion, ETIQUETAS_EJECUCION } from '@/lib/formato'

const COLOR_ESTADO: Record<string, string> = {
  COMPLETADO: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300',
  COMPLETADO_CON_ERRORES: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300',
  CANCELADO: 'bg-gray-100 text-gray-500 dark:bg-gray-700 dark:text-gray-400',
  FALLIDO: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
}

interface FilaHistorialProps {
  item: ResumenHistorial
  seleccionado: boolean
  onClick: () => void
}

export function FilaHistorial({ item, seleccionado, onClick }: FilaHistorialProps) {
  return (
    <tr
      onClick={onClick}
      className={[
        'cursor-pointer transition-colors text-sm',
        seleccionado
          ? 'bg-blue-50 dark:bg-blue-900/30'
          : 'hover:bg-gray-50 dark:hover:bg-gray-800/50',
      ].join(' ')}
    >
      <td className="px-3 py-2 text-gray-600 dark:text-gray-400 tabular-nums">
        {formatearFecha(item.timestamp_inicio)}
      </td>
      <td className="px-3 py-2">
        <span className={`text-xs px-1.5 py-0.5 rounded font-medium ${COLOR_ESTADO[item.estado] ?? ''}`}>
          {ETIQUETAS_EJECUCION[item.estado] ?? item.estado}
        </span>
        {item.modo_prueba && (
          <span className="ml-1 text-xs text-gray-400 dark:text-gray-500">(prueba)</span>
        )}
      </td>
      <td className="px-3 py-2 text-gray-600 dark:text-gray-300 tabular-nums">
        {formatearDuracion(item.duracion_ejecucion)}
      </td>
      <td className="px-3 py-2 text-gray-500 dark:text-gray-400">
        {item.resumen ? (
          <>
            <span className="text-green-600 dark:text-green-400">+{item.resumen.nuevos}</span>
            {' '}
            <span className="text-blue-600 dark:text-blue-400">~{item.resumen.modificados}</span>
            {' '}
            <span className="text-red-600 dark:text-red-400">-{item.resumen.eliminados}</span>
          </>
        ) : (
          <span className="text-gray-400 dark:text-gray-600 text-xs">—</span>
        )}
      </td>
      <td className="px-3 py-2 text-gray-400 dark:text-gray-500 text-xs truncate max-w-[200px]" title={item.origen}>
        {item.origen.split(/[\\/]/).pop()}
      </td>
    </tr>
  )
}
