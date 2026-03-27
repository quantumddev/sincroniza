/**
 * PanelConfiguracion — controles de análisis y sincronización del perfil activo.
 */
import { useAppStore } from '@/state/useAppStore'
import { BotonAccion } from '@/components/BotonAccion'
import { SelectorRuta } from '@/components/SelectorRuta'
import { ETIQUETAS_METODO } from '@/lib/formato'
import { useCallback } from 'react'

interface PanelConfiguracionProps {
  onSolicitarSync: () => void
}

export function PanelConfiguracion({ onSolicitarSync }: PanelConfiguracionProps) {
  const {
    perfilActivo,
    estadoAnalisis,
    estadoSync,
    iniciarAnalisis,
    cancelarAnalisis,
    cancelarSync,
    setVista,
  } = useAppStore()
  const irAReglasPerfilActivo = useCallback(() => setVista('reglas_perfil'), [setVista])

  if (!perfilActivo) {
    return (
      <div className="text-sm text-gray-400 dark:text-gray-500 p-4">
        Selecciona un perfil en el panel lateral.
      </div>
    )
  }

  const analizando = estadoAnalisis === 'analizando'
  const sincronizando = estadoSync === 'ejecutando'
  const ocupado = analizando || sincronizando

  return (
    <div className="flex flex-col gap-3">
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <SelectorRuta
          id="cfg-origen"
          label="Origen"
          valor={perfilActivo.origen}
          onChange={() => {/* sólo lectura en este panel; editar desde Perfiles */}}
          placeholder="No definido"
          titulo="Seleccionar origen"
          disabled
        />
        <SelectorRuta
          id="cfg-destino"
          label="Destino"
          valor={perfilActivo.destino}
          onChange={() => {}}
          placeholder="No definido"
          titulo="Seleccionar destino"
          disabled
        />
      </div>

      <div className="flex items-center gap-3 flex-wrap">
        <div className="flex items-center gap-2">
          <label className="text-xs font-medium text-gray-600 dark:text-gray-400">Método</label>
          <span className="text-xs px-2 py-1 rounded bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
            {ETIQUETAS_METODO[perfilActivo.metodo_comparacion]}
          </span>
        </div>

        <div className="flex gap-2 ml-auto flex-wrap">
          <BotonAccion variante="secundario" onClick={irAReglasPerfilActivo} disabled={ocupado}>
            Reglas
          </BotonAccion>
          {sincronizando ? (
            <BotonAccion variante="peligro" onClick={cancelarSync}>
              Cancelar sync
            </BotonAccion>
          ) : analizando ? (
            <BotonAccion variante="peligro" onClick={cancelarAnalisis}>
              Cancelar análisis
            </BotonAccion>
          ) : (
            <>
              <BotonAccion
                variante="secundario"
                onClick={() => iniciarAnalisis(perfilActivo.id)}
                disabled={ocupado}
              >
                Modo prueba
              </BotonAccion>
              <BotonAccion
                onClick={() => iniciarAnalisis(perfilActivo.id)}
                disabled={ocupado}
                cargando={analizando}
              >
                Analizar
              </BotonAccion>
              <BotonAccion
                variante="primario"
                onClick={onSolicitarSync}
                disabled={ocupado}
              >
                Sincronizar
              </BotonAccion>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
