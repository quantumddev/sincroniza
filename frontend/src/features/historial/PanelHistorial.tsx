/**
 * PanelHistorial — lista paginada del historial de ejecuciones.
 * Al seleccionar una fila, carga el detalle completo.
 */
import { useEffect, useState } from 'react'
import type { ResultadoEjecucion } from '@/lib/tipos'
import { useAppStore } from '@/state/useAppStore'
import { llamarRpc } from '@/lib/rpc'
import { BotonAccion } from '@/components/BotonAccion'
import { FilaHistorial } from './FilaHistorial'
import { DetalleEjecucion } from './DetalleEjecucion'

const LIMITE = 20

export function PanelHistorial() {
  const { historial, totalHistorial, cargarHistorial, setVista } = useAppStore()
  const [pagina, setPagina] = useState(1)
  const [cargando, setCargando] = useState(false)
  const [seleccionadoId, setSeleccionadoId] = useState<string | null>(null)
  const [detalle, setDetalle] = useState<ResultadoEjecucion | null>(null)
  const [cargandoDetalle, setCargandoDetalle] = useState(false)

  useEffect(() => {
    setCargando(true)
    cargarHistorial(pagina, LIMITE).finally(() => setCargando(false))
  }, [pagina, cargarHistorial])

  const seleccionar = async (id: string) => {
    if (seleccionadoId === id) {
      setSeleccionadoId(null)
      setDetalle(null)
      return
    }
    setSeleccionadoId(id)
    setDetalle(null)
    setCargandoDetalle(true)
    try {
      const r = await llamarRpc<ResultadoEjecucion>('historial.obtener', { id })
      setDetalle(r)
    } finally {
      setCargandoDetalle(false)
    }
  }

  const totalPaginas = Math.ceil(totalHistorial / LIMITE)

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-gray-200 dark:border-gray-700">
        <button
          onClick={() => setVista('principal')}
          className="p-1 rounded text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
          title="Volver"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <h2 className="text-sm font-semibold text-gray-900 dark:text-gray-100 flex-1">
          Historial
        </h2>
      </div>

      <div className="flex-1 overflow-hidden flex flex-col">
        {cargando ? (
          <p className="p-4 text-sm text-gray-400">Cargando…</p>
        ) : historial.length === 0 ? (
          <p className="p-4 text-sm text-gray-400">No hay ejecuciones registradas.</p>
        ) : (
          <div className="flex-1 overflow-y-auto">
            <table className="w-full text-sm">
              <thead className="sticky top-0 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700">
                <tr className="text-left text-xs font-medium text-gray-500 dark:text-gray-400">
                  <th className="px-3 py-2">Fecha</th>
                  <th className="px-3 py-2">Estado</th>
                  <th className="px-3 py-2">Duración</th>
                  <th className="px-3 py-2">Cambios</th>
                  <th className="px-3 py-2">Origen</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                {historial.map(item => (
                  <FilaHistorial
                    key={item.id}
                    item={item}
                    seleccionado={item.id === seleccionadoId}
                    onClick={() => seleccionar(item.id)}
                  />
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Detalle */}
        {seleccionadoId && (
          <div className="border-t border-gray-200 dark:border-gray-700 overflow-y-auto max-h-64">
            {cargandoDetalle ? (
              <p className="p-4 text-sm text-gray-400">Cargando detalle…</p>
            ) : detalle ? (
              <DetalleEjecucion resultado={detalle} />
            ) : null}
          </div>
        )}

        {/* Paginación */}
        {totalPaginas > 1 && (
          <div className="flex items-center justify-between px-4 py-2 border-t border-gray-200 dark:border-gray-700 shrink-0">
            <BotonAccion
              variante="secundario"
              onClick={() => setPagina(p => Math.max(1, p - 1))}
              disabled={pagina === 1}
            >
              ← Anterior
            </BotonAccion>
            <span className="text-xs text-gray-500 dark:text-gray-400">
              Pág. {pagina} de {totalPaginas}
            </span>
            <BotonAccion
              variante="secundario"
              onClick={() => setPagina(p => Math.min(totalPaginas, p + 1))}
              disabled={pagina === totalPaginas}
            >
              Siguiente →
            </BotonAccion>
          </div>
        )}
      </div>
    </div>
  )
}
