/**
 * PanelReglas — gestión de reglas de exclusión globales.
 */
import { useEffect, useState } from 'react'
import type { Regla, TipoRegla } from '@/lib/tipos'
import { llamarRpc } from '@/lib/rpc'
import { useAppStore } from '@/state/useAppStore'
import { BotonAccion } from '@/components/BotonAccion'
import { EstadoVacio } from '@/components/EstadoVacio'
import { FilaRegla } from './FilaRegla'
import { FormularioRegla } from './FormularioRegla'

export function PanelReglas() {
  const { reglasGlobales, setVista } = useAppStore()
  const [reglas, setReglas] = useState<Regla[]>([])
  const [guardando, setGuardando] = useState(false)
  const [error, setError] = useState('')
  const [modificado, setModificado] = useState(false)

  useEffect(() => {
    setReglas(reglasGlobales)
  }, [reglasGlobales])

  const toggleRegla = (regla: Regla) => {
    setReglas(prev => prev.map(r => r.id === regla.id ? { ...r, activa: !r.activa } : r))
    setModificado(true)
  }

  const eliminarRegla = (regla: Regla) => {
    setReglas(prev => prev.filter(r => r.id !== regla.id))
    setModificado(true)
  }

  const agregarRegla = (patron: string, tipo: TipoRegla) => {
    const nueva: Regla = {
      id: `temp_${Date.now()}`,
      patron,
      tipo,
      activa: true,
      origen: 'USUARIO',
    }
    setReglas(prev => [...prev, nueva])
    setModificado(true)
  }

  const guardar = async () => {
    setGuardando(true)
    setError('')
    try {
      await llamarRpc('reglas.guardar', { reglas })
      setModificado(false)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error al guardar las reglas')
    } finally {
      setGuardando(false)
    }
  }

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
          Reglas de exclusión
        </h2>
        {modificado && (
          <BotonAccion onClick={guardar} cargando={guardando}>
            Guardar
          </BotonAccion>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-3 flex flex-col gap-2">
        <FormularioRegla onAgregar={agregarRegla} />

        {error && (
          <p className="text-sm text-red-600 dark:text-red-400 px-1">{error}</p>
        )}

        {reglas.length === 0 ? (
          <EstadoVacio
            titulo="Sin reglas"
            descripcion="No hay reglas de exclusión definidas. Los archivos y carpetas del sistema no se sincronizarán."
          />
        ) : (
          reglas.map(r => (
            <FilaRegla
              key={r.id}
              regla={r}
              onToggle={toggleRegla}
              onEliminar={eliminarRegla}
            />
          ))
        )}
      </div>
    </div>
  )
}
