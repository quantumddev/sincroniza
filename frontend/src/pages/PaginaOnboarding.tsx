/**
 * PaginaOnboarding — pantalla de bienvenida cuando no hay perfiles configurados.
 */
import { useState } from 'react'
import { FormularioPerfil } from '@/features/perfiles/FormularioPerfil'

interface PaginaOnboardingProps {
  onPerfilCreado: () => void
}

export function PaginaOnboarding({ onPerfilCreado }: PaginaOnboardingProps) {
  const [mostrarFormulario, setMostrarFormulario] = useState(false)

  if (mostrarFormulario) {
    return (
      <div className="flex items-center justify-center h-full p-8">
        <div className="w-full max-w-md rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 shadow-sm">
          <FormularioPerfil onCerrar={onPerfilCreado} />
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col items-center justify-center h-full gap-6 p-8 text-center">
      <div className="w-16 h-16 rounded-2xl bg-blue-50 dark:bg-blue-900/30 flex items-center justify-center">
        <svg className="w-8 h-8 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 7.5h-.75A2.25 2.25 0 004.5 9.75v7.5a2.25 2.25 0 002.25 2.25h7.5a2.25 2.25 0 002.25-2.25v-7.5a2.25 2.25 0 00-2.25-2.25h-.75m-6 3.75l3 3m0 0l3-3m-3 3V1.5m6 9h.75a2.25 2.25 0 012.25 2.25v7.5a2.25 2.25 0 01-2.25 2.25h-7.5a2.25 2.25 0 01-2.25-2.25v-.75" />
        </svg>
      </div>

      <div className="flex flex-col gap-2">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
          Bienvenido a Sincroniza
        </h1>
        <p className="text-gray-500 dark:text-gray-400 max-w-md">
          Sincroniza carpetas de forma rápida y segura. Crea tu primer perfil para indicar
          las carpetas de origen y destino que deseas mantener sincronizadas.
        </p>
      </div>

      <button
        onClick={() => setMostrarFormulario(true)}
        className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 transition-colors"
      >
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
        </svg>
        Crear primer perfil
      </button>
    </div>
  )
}
