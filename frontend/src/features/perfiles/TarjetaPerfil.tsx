/**
 * TarjetaPerfil — muestra los datos de un perfil y permite editarlo/eliminarlo.
 */
import { useState } from 'react'
import type { Perfil } from '@/lib/tipos'
import { llamarRpc } from '@/lib/rpc'
import { formatearFecha } from '@/lib/formato'
import { DialogoConfirmacion } from '@/components/DialogoConfirmacion'
import { useAppStore } from '@/state/useAppStore'

interface TarjetaPerfilProps {
  perfil: Perfil
  activo: boolean
  onEditar: (perfil: Perfil) => void
}

export function TarjetaPerfil({ perfil, activo, onEditar }: TarjetaPerfilProps) {
  const { cargarPerfiles, setPerfilActivo, perfilActivo } = useAppStore()
  const [eliminando, setEliminando] = useState(false)
  const [confirmar, setConfirmar] = useState(false)

  const seleccionar = () => setPerfilActivo(perfil)

  const eliminar = async () => {
    setEliminando(true)
    try {
      await llamarRpc('perfil.eliminar', { id: perfil.id })
      if (perfilActivo?.id === perfil.id) {
        setPerfilActivo(null)
      }
      await cargarPerfiles()
    } finally {
      setEliminando(false)
      setConfirmar(false)
    }
  }

  return (
    <>
      <div
        onClick={seleccionar}
        className={[
          'flex flex-col gap-1 p-3 rounded-lg cursor-pointer transition-colors border',
          activo
            ? 'bg-blue-50 border-blue-300 dark:bg-blue-900/30 dark:border-blue-600'
            : 'bg-white border-gray-200 hover:bg-gray-50 dark:bg-gray-800 dark:border-gray-700 dark:hover:bg-gray-750',
        ].join(' ')}
      >
        <div className="flex items-start justify-between gap-2">
          <span className={[
            'text-sm font-medium truncate',
            activo ? 'text-blue-700 dark:text-blue-300' : 'text-gray-900 dark:text-gray-100',
          ].join(' ')}>
            {perfil.nombre}
          </span>
          <div className="flex gap-1 shrink-0" onClick={e => e.stopPropagation()}>
            <button
              onClick={() => onEditar(perfil)}
              className="p-1 rounded text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
              title="Editar perfil"
            >
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M15.232 5.232l3.536 3.536M9 11l6.536-6.536a2 2 0 012.828 0l.172.172a2 2 0 010 2.828L12 13.5H9v-2.5z" />
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 20h18" />
              </svg>
            </button>
            <button
              onClick={() => setConfirmar(true)}
              className="p-1 rounded text-gray-400 hover:text-red-500 dark:hover:text-red-400 transition-colors"
              title="Eliminar perfil"
            >
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>
        <p className="text-xs text-gray-500 dark:text-gray-400 truncate" title={perfil.origen}>
          <span className="font-medium">O:</span> {perfil.origen || <em>sin definir</em>}
        </p>
        <p className="text-xs text-gray-500 dark:text-gray-400 truncate" title={perfil.destino}>
          <span className="font-medium">D:</span> {perfil.destino || <em>sin definir</em>}
        </p>
        {perfil.ultima_ejecucion && (
          <p className="text-xs text-gray-400 dark:text-gray-500">
            Última: {formatearFecha(perfil.ultima_ejecucion)}
          </p>
        )}
      </div>

      <DialogoConfirmacion
        abierto={confirmar}
        titulo="Eliminar perfil"
        textoConfirmar="Eliminar"
        cargando={eliminando}
        onConfirmar={eliminar}
        onCancelar={() => setConfirmar(false)}
      >
        <p className="text-sm text-gray-600 dark:text-gray-400">
          ¿Seguro que deseas eliminar el perfil <strong>«{perfil.nombre}»</strong>?
          Esta acción no se puede deshacer.
        </p>
      </DialogoConfirmacion>
    </>
  )
}
