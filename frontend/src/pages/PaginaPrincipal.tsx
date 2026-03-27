/**
 * PaginaPrincipal — pantalla principal con la configuración del análisis,
 * el árbol de diferencias y el panel de log.
 */
import { useState } from 'react'
import { useAppStore } from '@/state/useAppStore'
import { PanelConfiguracion } from '@/features/analisis/PanelConfiguracion'
import { PanelResumen } from '@/features/analisis/PanelResumen'
import { BarraProgreso } from '@/features/analisis/BarraProgreso'
import { ArbolDiferencias } from '@/features/arbol/ArbolDiferencias'
import { PanelLog } from '@/features/log/PanelLog'
import { DialogoConfirmacion } from '@/components/DialogoConfirmacion'

export function PaginaPrincipal() {
  const {
    perfilActivo,
    estadoAnalisis,
    estadoSync,
    planActual,
    progresoSync,
    mensajeProgreso,
    iniciarSync,
    cancelarSync,
  } = useAppStore()

  const [confirmarSync, setConfirmarSync] = useState(false)
  const [ejecutandoSync, setEjecutandoSync] = useState(false)

  const ejecutarSync = async () => {
    if (!planActual) return
    setEjecutandoSync(true)
    try {
      await iniciarSync(planActual.id, false)
    } finally {
      setEjecutandoSync(false)
      setConfirmarSync(false)
    }
  }

  const analizando = estadoAnalisis === 'analizando'
  const sincronizando = estadoSync === 'ejecutando'

  const progresoPct = progresoSync && progresoSync.total > 0
    ? Math.round((progresoSync.completadas / progresoSync.total) * 100)
    : 0

  return (
    <div className="h-full flex flex-col overflow-hidden">
      {/* Configuración */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700 shrink-0">
        <PanelConfiguracion onSolicitarSync={() => setConfirmarSync(true)} />
      </div>

      {/* Barra de progreso */}
      {(analizando || sincronizando) && (
        <div className="px-4 py-2 shrink-0">
          <BarraProgreso
            porcentaje={sincronizando ? progresoPct : 0}
            mensaje={sincronizando
              ? progresoSync
                ? `${progresoSync.completadas} / ${progresoSync.total} archivos…`
                : 'Sincronizando…'
              : mensajeProgreso || 'Analizando…'
            }
            color={sincronizando ? 'green' : 'blue'}
          />
        </div>
      )}

      {/* Resumen del plan */}
      {planActual && estadoAnalisis === 'completado' && (
        <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700 shrink-0">
          <PanelResumen plan={planActual} />
        </div>
      )}

      {/* Árbol de diferencias */}
      <div className="flex-1 overflow-hidden px-4 py-3">
        {perfilActivo ? (
          <ArbolDiferencias />
        ) : (
          <div className="h-full flex items-center justify-center text-sm text-gray-400 dark:text-gray-500">
            Selecciona un perfil para ver las diferencias.
          </div>
        )}
      </div>

      {/* Log */}
      <PanelLog />

      {/* Diálogo de confirmación de sincronización */}
      <DialogoConfirmacion
        abierto={confirmarSync}
        titulo="Confirmar sincronización"
        textoConfirmar="Sincronizar ahora"
        cargando={ejecutandoSync}
        onConfirmar={ejecutarSync}
        onCancelar={() => {
          if (!ejecutandoSync) setConfirmarSync(false)
        }}
      >
        <div className="flex flex-col gap-2 text-sm text-gray-600 dark:text-gray-400">
          <p>
            Se van a realizar los cambios del análisis en el destino.
            Esta operación puede sobrescribir o eliminar archivos.
          </p>
          {planActual && (
            <div className="flex gap-4 text-xs bg-gray-50 dark:bg-gray-800 rounded p-2">
              <span className="text-green-600 dark:text-green-400">
                +{planActual.resumen.nuevos} nuevos
              </span>
              <span className="text-blue-600 dark:text-blue-400">
                ~{planActual.resumen.modificados} modificados
              </span>
              <span className="text-red-600 dark:text-red-400">
                -{planActual.resumen.eliminados} eliminados
              </span>
            </div>
          )}
          {sincronizando && (
            <button
              onClick={cancelarSync}
              className="text-red-600 dark:text-red-400 underline text-xs"
            >
              Cancelar sincronización en curso
            </button>
          )}
        </div>
      </DialogoConfirmacion>
    </div>
  )
}
