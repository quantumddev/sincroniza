/**
 * EntradaLog — fila de un evento del log.
 */
import type { EventoLog, NivelLog } from '@/lib/tipos'
import { formatearHora } from '@/lib/formato'

const ESTILOS_NIVEL: Record<NivelLog, string> = {
  INFO: 'bg-sky-100 text-sky-600 dark:bg-sky-900/30 dark:text-sky-400',
  WARNING: 'bg-amber-100 text-amber-600 dark:bg-amber-900/30 dark:text-amber-400',
  ERROR: 'bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400',
}

interface EntradaLogProps {
  evento: EventoLog
}

export function EntradaLog({ evento }: EntradaLogProps) {
  return (
    <div className="flex items-start gap-2 py-0.5 text-xs hover:bg-gray-50 dark:hover:bg-gray-800/50 px-2 rounded">
      <span className="text-gray-400 dark:text-gray-500 shrink-0 tabular-nums">
        {formatearHora(evento.timestamp)}
      </span>
      <span className={`px-1.5 py-0 rounded font-medium shrink-0 ${ESTILOS_NIVEL[evento.nivel]}`}>
        {evento.nivel}
      </span>
      <span className="text-gray-700 dark:text-gray-300 break-all leading-relaxed">
        {evento.mensaje}
      </span>
    </div>
  )
}
