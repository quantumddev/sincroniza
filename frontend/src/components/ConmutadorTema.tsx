/**
 * ConmutadorTema — botón toggle claro/oscuro.
 */
import { useTemaStore } from '@/state/useTemaStore'

export function ConmutadorTema() {
  const { tema, alternar } = useTemaStore()
  const esOscuro = tema === 'oscuro'

  return (
    <button
      type="button"
      onClick={alternar}
      title={esOscuro ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'}
      aria-label={esOscuro ? 'Modo claro' : 'Modo oscuro'}
      className="flex items-center justify-center w-8 h-8 rounded-md
                 text-gray-500 hover:text-gray-700 hover:bg-gray-100
                 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-700
                 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
    >
      {esOscuro ? (
        // Sol (modo claro)
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.8} stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round"
            d="M12 3v2m0 14v2M4.22 4.22l1.42 1.42m12.72 12.72 1.42 1.42M3 12H1m22 0h-2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42M12 7a5 5 0 1 0 0 10A5 5 0 0 0 12 7z" />
        </svg>
      ) : (
        // Luna (modo oscuro)
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.8} stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round"
            d="M21.752 15.002A9.72 9.72 0 0 1 18 15.75 9.75 9.75 0 0 1 8.25 6 9.77 9.77 0 0 1 8.998 2.248 9.75 9.75 0 0 0 12 22a9.74 9.74 0 0 0 9.752-6.998z" />
        </svg>
      )}
    </button>
  )
}
