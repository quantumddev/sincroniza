/**
 * Sidebar — panel lateral de navegación y perfiles.
 */
import { useAppStore } from '@/state/useAppStore'
import type { Perfil } from '@/lib/tipos'

interface SidebarProps {
  onNuevoPerfil: () => void
  onGestionarReglas: () => void
  onVerHistorial: () => void
}

function IconoSync({ className = 'w-4 h-4' }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" strokeWidth={1.8} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round"
        d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99" />
    </svg>
  )
}

function TarjetaPerfil({ perfil, activo, onClick }: {
  perfil: Perfil
  activo: boolean
  onClick: () => void
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={[
        'w-full text-left px-3 py-2 rounded-lg text-sm transition-colors group',
        activo
          ? 'bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300'
          : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700',
      ].join(' ')}
    >
      <div className="font-medium truncate">{perfil.nombre}</div>
      <div className="text-xs truncate mt-0.5 opacity-70 font-mono">{perfil.origen}</div>
    </button>
  )
}

export function Sidebar({ onNuevoPerfil, onGestionarReglas, onVerHistorial }: SidebarProps) {
  const { perfiles, perfilActivo, setPerfilActivo, vistaActual, setVista } = useAppStore()

  const handleVerHistorial = () => {
    setVista('historial')
    onVerHistorial()
  }

  const handleGestionarReglas = () => {
    setVista('reglas')
    onGestionarReglas()
  }

  return (
    <aside className="w-56 flex flex-col border-r border-gray-200 dark:border-gray-700
                      bg-gray-50 dark:bg-gray-800/50 flex-shrink-0">
      {/* Logo */}
      <div className="h-12 flex items-center gap-2 px-4 border-b border-gray-200 dark:border-gray-700">
        <IconoSync className="w-5 h-5 text-blue-600 dark:text-blue-400" />
        <span className="font-bold text-gray-900 dark:text-gray-100 text-base">Sincroniza</span>
      </div>

      {/* Perfiles */}
      <div className="flex-1 overflow-y-auto py-2 px-2">
        <div className="flex items-center justify-between px-1 mb-1">
          <span className="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wide">
            Perfiles
          </span>
          <button
            type="button"
            onClick={onNuevoPerfil}
            title="Nuevo perfil"
            aria-label="Nuevo perfil"
            className="text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
            </svg>
          </button>
        </div>

        {perfiles.length === 0 ? (
          <p className="text-xs text-gray-400 dark:text-gray-500 px-1 py-2">
            No hay perfiles. Crea uno.
          </p>
        ) : (
          <div className="flex flex-col gap-0.5">
            {perfiles.map(p => (
              <TarjetaPerfil
                key={p.id}
                perfil={p}
                activo={perfilActivo?.id === p.id && vistaActual === 'principal'}
                onClick={() => { setPerfilActivo(p); setVista('principal') }}
              />
            ))}
          </div>
        )}
      </div>

      {/* Navegación inferior */}
      <div className="border-t border-gray-200 dark:border-gray-700 py-1 px-2">
        <NavItem
          activo={vistaActual === 'historial'}
          onClick={handleVerHistorial}
          icono={
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.8} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round"
                d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0z" />
            </svg>
          }
        >
          Historial
        </NavItem>
        <NavItem
          activo={vistaActual === 'reglas'}
          onClick={handleGestionarReglas}
          icono={
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.8} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round"
                d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0z" />
            </svg>
          }
        >
          Reglas
        </NavItem>
      </div>
    </aside>
  )
}

function NavItem({
  activo,
  onClick,
  icono,
  children,
}: {
  activo: boolean
  onClick: () => void
  icono: React.ReactNode
  children: React.ReactNode
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={[
        'w-full flex items-center gap-2 px-2 py-1.5 rounded-md text-sm transition-colors',
        activo
          ? 'bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300'
          : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700',
      ].join(' ')}
    >
      {icono}
      {children}
    </button>
  )
}
