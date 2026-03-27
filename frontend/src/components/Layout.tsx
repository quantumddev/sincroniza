/**
 * Layout — shell principal de la aplicación.
 * Estructura: barra superior + sidebar izquierdo + zona central.
 */
import type { ReactNode } from 'react'
import { ConmutadorTema } from '@/components/ConmutadorTema'
import { Sidebar } from '@/components/Sidebar'
import { useAppStore } from '@/state/useAppStore'

interface LayoutProps {
  children: ReactNode
  onNuevoPerfil: () => void
  onGestionarReglas: () => void
  onVerHistorial: () => void
}

export function Layout({
  children,
  onNuevoPerfil,
  onGestionarReglas,
  onVerHistorial,
}: LayoutProps) {
  const { perfilActivo } = useAppStore()

  return (
    <div className="flex flex-col h-screen bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100">
      {/* Barra superior */}
      <header className="h-12 flex items-center justify-between px-4
                         border-b border-gray-200 dark:border-gray-700
                         bg-white dark:bg-gray-900 flex-shrink-0 z-10">
        <div className="flex items-center gap-3">
          {perfilActivo && (
            <span className="text-sm text-gray-500 dark:text-gray-400">
              Perfil activo:&nbsp;
              <strong className="text-gray-700 dark:text-gray-200">{perfilActivo.nombre}</strong>
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <ConmutadorTema />
        </div>
      </header>

      {/* Cuerpo principal */}
      <div className="flex flex-1 overflow-hidden">
        <Sidebar
          onNuevoPerfil={onNuevoPerfil}
          onGestionarReglas={onGestionarReglas}
          onVerHistorial={onVerHistorial}
        />
        <main className="flex-1 overflow-hidden">
          {children}
        </main>
      </div>
    </div>
  )
}
