/**
 * PanelResumen — cuadrícula de conteos del plan de sincronización.
 */
import type { PlanSincronizacion } from '@/lib/tipos'
import { formatearTamano, pluralizar } from '@/lib/formato'

interface PanelResumenProps {
  plan: PlanSincronizacion
}

interface TarjetaConteoProps {
  etiqueta: string
  valor: number
  color: string
}

function TarjetaConteo({ etiqueta, valor, color }: TarjetaConteoProps) {
  return (
    <div className={`flex flex-col items-center p-3 rounded-lg border ${color}`}>
      <span className="text-xl font-bold">{valor}</span>
      <span className="text-xs mt-0.5">{etiqueta}</span>
    </div>
  )
}

export function PanelResumen({ plan }: PanelResumenProps) {
  const r = plan.resumen

  return (
    <div className="flex flex-col gap-3">
      <div className="grid grid-cols-3 gap-2 sm:grid-cols-6">
        <TarjetaConteo etiqueta="Nuevos" valor={r.nuevos} color="bg-green-50 border-green-200 text-green-700 dark:bg-green-900/20 dark:border-green-800 dark:text-green-300" />
        <TarjetaConteo etiqueta="Modificados" valor={r.modificados} color="bg-blue-50 border-blue-200 text-blue-700 dark:bg-blue-900/20 dark:border-blue-800 dark:text-blue-300" />
        <TarjetaConteo etiqueta="Eliminados" valor={r.eliminados} color="bg-red-50 border-red-200 text-red-700 dark:bg-red-900/20 dark:border-red-800 dark:text-red-300" />
        <TarjetaConteo etiqueta="Idénticos" valor={r.identicos} color="bg-gray-50 border-gray-200 text-gray-600 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-400" />
        <TarjetaConteo etiqueta="Excluidos" valor={r.excluidos} color="bg-yellow-50 border-yellow-200 text-yellow-700 dark:bg-yellow-900/20 dark:border-yellow-800 dark:text-yellow-300" />
        <TarjetaConteo etiqueta="Errores" valor={r.errores} color="bg-orange-50 border-orange-200 text-orange-700 dark:bg-orange-900/20 dark:border-orange-800 dark:text-orange-300" />
      </div>

      <div className="flex flex-wrap gap-4 text-xs text-gray-500 dark:text-gray-400 px-1">
        <span>Operaciones: <strong className="text-gray-700 dark:text-gray-300">{pluralizar(plan.operaciones.length, 'operación', 'operaciones')}</strong></span>
        {(r.tamaño_copiar + r.tamaño_reemplazar) > 0 && (
          <span>Tamaño a copiar: <strong className="text-gray-700 dark:text-gray-300">{formatearTamano(r.tamaño_copiar + r.tamaño_reemplazar)}</strong></span>
        )}
        {r.eliminados > 0 && (
          <span className="text-gray-500 dark:text-gray-400">
            Eliminados: <strong className="text-red-600 dark:text-red-400">{r.eliminados}</strong>
          </span>
        )}
      </div>
    </div>
  )
}
