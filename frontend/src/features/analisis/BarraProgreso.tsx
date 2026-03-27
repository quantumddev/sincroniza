/**
 * BarraProgreso — barra de progreso lineal con mensaje.
 */
interface BarraProgresoProps {
  porcentaje: number   // 0-100
  mensaje?: string
  color?: 'blue' | 'green' | 'amber' | 'red'
}

const COLORES = {
  blue: 'bg-blue-500',
  green: 'bg-green-500',
  amber: 'bg-amber-500',
  red: 'bg-red-500',
}

export function BarraProgreso({ porcentaje, mensaje, color = 'blue' }: BarraProgresoProps) {
  const pct = Math.min(100, Math.max(0, porcentaje))
  return (
    <div className="flex flex-col gap-1">
      {mensaje && (
        <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{mensaje}</p>
      )}
      <div className="h-2 w-full bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-300 ${COLORES[color]}`}
          style={{ width: `${pct}%` }}
          role="progressbar"
          aria-valuenow={pct}
          aria-valuemin={0}
          aria-valuemax={100}
        />
      </div>
    </div>
  )
}
