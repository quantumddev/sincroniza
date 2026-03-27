/**
 * DialogoConfirmacion — modal de confirmación genérico y específico de sync.
 */
import type { ReactNode } from 'react'
import { BotonAccion } from '@/components/BotonAccion'

interface DialogoConfirmacionProps {
  abierto: boolean
  titulo: string
  children: ReactNode
  textoCancelar?: string
  textoConfirmar?: string
  varianteConfirmar?: 'primario' | 'peligro'
  onCancelar: () => void
  onConfirmar: () => void
  confirmacionRequerida?: boolean
  cargando?: boolean
}

export function DialogoConfirmacion({
  abierto,
  titulo,
  children,
  textoCancelar = 'Cancelar',
  textoConfirmar = 'Confirmar',
  varianteConfirmar = 'primario',
  onCancelar,
  onConfirmar,
  confirmacionRequerida = false,
  cargando = false,
}: DialogoConfirmacionProps) {
  if (!abierto) return null

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      role="dialog"
      aria-modal="true"
      aria-labelledby="dialogo-titulo"
    >
      {/* Overlay */}
      <div
        className="absolute inset-0 bg-black/40 dark:bg-black/60"
        onClick={onCancelar}
        aria-hidden="true"
      />

      {/* Panel */}
      <div className="relative z-10 w-full max-w-md mx-4 bg-white dark:bg-gray-800
                      rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700
                      overflow-hidden">
        {/* Cabecera */}
        <div className="px-5 py-4 border-b border-gray-200 dark:border-gray-700">
          <h2 id="dialogo-titulo" className="text-base font-semibold text-gray-900 dark:text-gray-100">
            {titulo}
          </h2>
        </div>

        {/* Cuerpo */}
        <div className="px-5 py-4 text-sm text-gray-600 dark:text-gray-300">
          {children}
        </div>

        {/* Pie */}
        <div className="px-5 py-4 border-t border-gray-200 dark:border-gray-700 flex justify-end gap-2">
          <BotonAccion variante="secundario" onClick={onCancelar} disabled={cargando}>
            {textoCancelar}
          </BotonAccion>
          <BotonAccion
            variante={varianteConfirmar}
            onClick={onConfirmar}
            disabled={confirmacionRequerida || cargando}
            cargando={cargando}
          >
            {textoConfirmar}
          </BotonAccion>
        </div>
      </div>
    </div>
  )
}
