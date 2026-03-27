/**
 * PanelPerfiles — gestión completa de perfiles (listado + formulario inline).
 */
import { useState } from 'react'
import type { Perfil } from '@/lib/tipos'
import { useAppStore } from '@/state/useAppStore'
import { BotonAccion } from '@/components/BotonAccion'
import { EstadoVacio } from '@/components/EstadoVacio'
import { TarjetaPerfil } from './TarjetaPerfil'
import { FormularioPerfil } from './FormularioPerfil'

export function PanelPerfiles() {
  const { perfiles, perfilActivo } = useAppStore()
  const [editando, setEditando] = useState<Perfil | null | 'nuevo'>(null)

  const mostrarFormulario = editando !== null

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Perfiles</h2>
        {!mostrarFormulario && (
          <BotonAccion
            variante="primario"
            onClick={() => setEditando('nuevo')}
            icono={
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
              </svg>
            }
          >
            Nuevo
          </BotonAccion>
        )}
      </div>

      {mostrarFormulario ? (
        <div className="flex-1 overflow-y-auto">
          <FormularioPerfil
            perfilEditar={editando !== 'nuevo' ? editando : undefined}
            onCerrar={() => setEditando(null)}
          />
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto p-3 flex flex-col gap-2">
          {perfiles.length === 0 ? (
            <EstadoVacio
              titulo="Sin perfiles"
              descripcion="Crea un perfil para comenzar a sincronizar carpetas."
              accion={
                <button
                  onClick={() => setEditando('nuevo')}
                  className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
                >
                  Crear perfil
                </button>
              }
            />
          ) : (
            perfiles.map(p => (
              <TarjetaPerfil
                key={p.id}
                perfil={p}
                activo={perfilActivo?.id === p.id}
                onEditar={setEditando}
              />
            ))
          )}
        </div>
      )}
    </div>
  )
}
