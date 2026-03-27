/**
 * DetalleEjecucion — vista detallada de un resultado del historial.
 */
import type { ResultadoEjecucion } from '@/lib/tipos'
import { formatearFecha, formatearDuracion, formatearTamano, ETIQUETAS_EJECUCION } from '@/lib/formato'

interface DetalleEjecucionProps {
  resultado: ResultadoEjecucion
}

export function DetalleEjecucion({ resultado: r }: DetalleEjecucionProps) {
  const res = r.resumen
  return (
    <div className="p-4 flex flex-col gap-4 text-sm">
      <div className="flex items-center gap-2 flex-wrap">
        <span className="font-medium text-gray-800 dark:text-gray-200">
          {ETIQUETAS_EJECUCION[r.estado]}
        </span>
        {r.modo_prueba && (
          <span className="text-xs bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 px-2 py-0.5 rounded">
            Modo prueba
          </span>
        )}
      </div>

      <div className="grid grid-cols-2 gap-x-6 gap-y-1 text-xs text-gray-600 dark:text-gray-400">
        <span>Inicio:</span>      <span className="text-gray-800 dark:text-gray-200">{formatearFecha(r.timestamp_inicio)}</span>
        <span>Fin:</span>         <span className="text-gray-800 dark:text-gray-200">{formatearFecha(r.timestamp_fin)}</span>
        <span>Duración:</span>    <span className="text-gray-800 dark:text-gray-200">{formatearDuracion(r.duracion_ejecucion)}</span>
        <span>Origen:</span>      <span className="text-gray-800 dark:text-gray-200 break-all">{r.origen}</span>
        <span>Destino:</span>     <span className="text-gray-800 dark:text-gray-200 break-all">{r.destino}</span>
      </div>

      <div className="grid grid-cols-3 gap-2">
        {[
          { lbl: 'Nuevos', val: res.nuevos, c: 'text-green-600 dark:text-green-400' },
          { lbl: 'Modificados', val: res.modificados, c: 'text-blue-600 dark:text-blue-400' },
          { lbl: 'Eliminados', val: res.eliminados, c: 'text-red-600 dark:text-red-400' },
          { lbl: 'Idénticos', val: res.identicos, c: 'text-gray-500 dark:text-gray-400' },
          { lbl: 'Excluidos', val: res.excluidos, c: 'text-yellow-600 dark:text-yellow-400' },
          { lbl: 'Errores', val: res.errores, c: 'text-orange-600 dark:text-orange-400' },
        ].map(({ lbl, val, c }) => (
          <div key={lbl} className="flex flex-col items-center p-2 rounded bg-gray-50 dark:bg-gray-800">
            <span className={`font-bold text-lg ${c}`}>{val}</span>
            <span className="text-xs text-gray-500 dark:text-gray-400">{lbl}</span>
          </div>
        ))}
      </div>

      {res.tamaño_copiar > 0 && (
        <p className="text-xs text-gray-500 dark:text-gray-400">
          Datos copiados: <strong>{formatearTamano(res.tamaño_copiar + res.tamaño_reemplazar)}</strong>
        </p>
      )}

      {r.errores.length > 0 && (
        <div className="flex flex-col gap-1">
          <p className="text-xs font-medium text-red-600 dark:text-red-400">Errores ({r.errores.length})</p>
          <div className="max-h-32 overflow-y-auto text-xs rounded bg-red-50 dark:bg-red-900/20 p-2 flex flex-col gap-1">
            {r.errores.map((e, i) => (
              <div key={i} className="text-red-700 dark:text-red-300">
                <span className="font-mono">{e.ruta}</span> — {e.mensaje}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
