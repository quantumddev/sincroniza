/**
 * BotonAccion — botón reutilizable con variantes y estados.
 */
import type { ButtonHTMLAttributes, ReactNode } from 'react'

type Variante = 'primario' | 'secundario' | 'peligro' | 'fantasma'

interface BotonAccionProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variante?: Variante
  cargando?: boolean
  icono?: ReactNode
  children: ReactNode
}

const CLASES: Record<Variante, string> = {
  primario:
    'bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800 dark:bg-blue-500 dark:hover:bg-blue-600',
  secundario:
    'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600',
  peligro:
    'bg-red-600 text-white hover:bg-red-700 active:bg-red-800 dark:bg-red-700 dark:hover:bg-red-600',
  fantasma:
    'bg-transparent text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700',
}

export function BotonAccion({
  variante = 'primario',
  cargando = false,
  icono,
  children,
  className = '',
  disabled,
  ...rest
}: BotonAccionProps) {
  const deshabilitado = disabled || cargando

  return (
    <button
      {...rest}
      disabled={deshabilitado}
      className={[
        'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium',
        'transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        CLASES[variante],
        className,
      ].join(' ')}
    >
      {cargando ? (
        <svg
          className="w-3.5 h-3.5 animate-spin"
          fill="none"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
          />
        </svg>
      ) : icono ? (
        <span className="flex-shrink-0">{icono}</span>
      ) : null}
      {children}
    </button>
  )
}
