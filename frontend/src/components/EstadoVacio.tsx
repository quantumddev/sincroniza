/**
 * EstadoVacio — placeholder para listas/áreas vacías.
 */
interface EstadoVacioProps {
  icono?: React.ReactNode
  titulo: string
  descripcion?: string
  accion?: React.ReactNode
}

export function EstadoVacio({ icono, titulo, descripcion, accion }: EstadoVacioProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-6 text-center gap-3">
      {icono && (
        <div className="text-gray-300 dark:text-gray-600 text-4xl mb-1">{icono}</div>
      )}
      <p className="font-medium text-gray-600 dark:text-gray-300">{titulo}</p>
      {descripcion && (
        <p className="text-sm text-gray-400 dark:text-gray-500 max-w-sm">{descripcion}</p>
      )}
      {accion && <div className="mt-2">{accion}</div>}
    </div>
  )
}
