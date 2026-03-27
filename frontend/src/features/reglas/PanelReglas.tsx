/**
 * PanelReglas — gestión de reglas de exclusión.
 *
 * Modo global (sin prop `perfil`): edita las reglas globales vía `reglas.guardar`.
 * Modo perfil (con prop `perfil`): edita las `reglas_propias` del perfil activo
 * y los IDs de reglas globales habilitadas para ese perfil (`reglas_exclusion_ids`).
 */
import { useEffect, useState } from 'react'
import type { Perfil, Regla, TipoRegla } from '@/lib/tipos'
import { llamarRpc } from '@/lib/rpc'
import { useAppStore } from '@/state/useAppStore'
import { BotonAccion } from '@/components/BotonAccion'
import { EstadoVacio } from '@/components/EstadoVacio'
import { FilaRegla } from './FilaRegla'
import { FormularioRegla } from './FormularioRegla'

interface PanelReglasProps {
  /** Si se proporciona, el panel edita las reglas propias del perfil en lugar de las globales. */
  perfil?: Perfil
}

export function PanelReglas({ perfil }: PanelReglasProps) {
  const { reglasGlobales, setVista, actualizarPerfil, cargarReglas } = useAppStore()

  // ── Modo global ────────────────────────────────────────────────────────────
  const [reglasGlobal, setReglasGlobal] = useState<Regla[]>([])

  // ── Modo perfil ────────────────────────────────────────────────────────────
  // reglas propias del perfil (CRUD completo)
  const [reglasPropia, setReglasPropia] = useState<Regla[]>(perfil?.reglas_propias ?? [])
  // IDs de reglas globales activas para este perfil
  const [idsActivos, setIdsActivos] = useState<Set<string>>(
    new Set(perfil?.reglas_exclusion_ids ?? []),
  )

  const [guardando, setGuardando] = useState(false)
  const [error, setError] = useState('')
  const [modificado, setModificado] = useState(false)

  // Inicializar reglas globales locales
  useEffect(() => {
    setReglasGlobal(reglasGlobales)
  }, [reglasGlobales])

  // ── Handlers modo global ───────────────────────────────────────────────────

  const toggleGlobal = (regla: Regla) => {
    setReglasGlobal(prev => prev.map(r => r.id === regla.id ? { ...r, activa: !r.activa } : r))
    setModificado(true)
  }

  const eliminarGlobal = (regla: Regla) => {
    setReglasGlobal(prev => prev.filter(r => r.id !== regla.id))
    setModificado(true)
  }

  const agregarGlobal = (patron: string, tipo: TipoRegla) => {
    setReglasGlobal(prev => [...prev, { id: `tmp_${Date.now()}`, patron, tipo, activa: true, origen: 'USUARIO' }])
    setModificado(true)
  }

  const guardarGlobal = async () => {
    setGuardando(true); setError('')
    try {
      await llamarRpc('reglas.guardar', { reglas: reglasGlobal })
      await cargarReglas()
      setModificado(false)
    } catch (e) { setError(e instanceof Error ? e.message : 'Error al guardar') }
    finally { setGuardando(false) }
  }

  // ── Handlers modo perfil ───────────────────────────────────────────────────

  const toggleIdActivo = (id: string) => {
    setIdsActivos(prev => {
      const n = new Set(prev)
      n.has(id) ? n.delete(id) : n.add(id)
      return n
    })
    setModificado(true)
  }

  const togglePropia = (regla: Regla) => {
    setReglasPropia(prev => prev.map(r => r.id === regla.id ? { ...r, activa: !r.activa } : r))
    setModificado(true)
  }

  const eliminarPropia = (regla: Regla) => {
    setReglasPropia(prev => prev.filter(r => r.id !== regla.id))
    setModificado(true)
  }

  const agregarPropia = (patron: string, tipo: TipoRegla) => {
    setReglasPropia(prev => [...prev, { id: `tmp_${Date.now()}`, patron, tipo, activa: true, origen: 'USUARIO' }])
    setModificado(true)
  }

  const guardarPerfil = async () => {
    if (!perfil) return
    setGuardando(true); setError('')
    try {
      const actualizado = await llamarRpc<Perfil>('perfil.actualizar', {
        id: perfil.id,
        cambios: {
          reglas_propias: reglasPropia.map(r => ({ ...r })),
          reglas_exclusion_ids: Array.from(idsActivos),
        },
      })
      actualizarPerfil(actualizado)
      setModificado(false)
    } catch (e) { setError(e instanceof Error ? e.message : 'Error al guardar') }
    finally { setGuardando(false) }
  }

  // ── Render ─────────────────────────────────────────────────────────────────

  const titulo = perfil ? `Reglas: ${perfil.nombre}` : 'Reglas de exclusión'
  const vistaAnterior = perfil ? 'principal' : 'principal'

  return (
    <div className="h-full flex flex-col">
      {/* Cabecera */}
      <div className="flex items-center gap-2 px-4 py-3 border-b border-gray-200 dark:border-gray-700">
        <button
          onClick={() => setVista(vistaAnterior)}
          className="p-1 rounded text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
          title="Volver"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <h2 className="text-sm font-semibold text-gray-900 dark:text-gray-100 flex-1 truncate">
          {titulo}
        </h2>
        {modificado && (
          <BotonAccion onClick={perfil ? guardarPerfil : guardarGlobal} cargando={guardando}>
            Guardar
          </BotonAccion>
        )}
      </div>

      <div className="flex-1 overflow-y-auto">
        {perfil ? (
          /* ── Modo perfil ──────────────────────────────────────────────── */
          <div className="p-3 flex flex-col gap-4">
            {error && <p className="text-sm text-red-600 dark:text-red-400">{error}</p>}

            {/* Reglas propias del perfil */}
            <section className="flex flex-col gap-2">
              <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">
                Reglas exclusivas de este perfil
              </h3>
              <FormularioRegla onAgregar={agregarPropia} />
              {reglasPropia.length === 0 ? (
                <EstadoVacio
                  titulo="Sin reglas propias"
                  descripcion="Añade reglas específicas para este perfil."
                />
              ) : (
                reglasPropia.map(r => (
                  <FilaRegla key={r.id} regla={r} onToggle={togglePropia} onEliminar={eliminarPropia} />
                ))
              )}
            </section>

            {/* Reglas globales habilitadas para este perfil */}
            <section className="flex flex-col gap-2">
              <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">
                Reglas globales activas en este perfil
              </h3>
              {reglasGlobales.length === 0 ? (
                <p className="text-xs text-gray-400 dark:text-gray-500">Sin reglas globales definidas.</p>
              ) : (
                reglasGlobales.map(r => {
                  const activa = idsActivos.has(r.id)
                  return (
                    <div
                      key={r.id}
                      onClick={() => { toggleIdActivo(r.id) }}
                      className={[
                        'flex items-center gap-2 px-3 py-2 rounded-md border cursor-pointer transition-colors select-none',
                        activa
                          ? 'bg-white border-gray-200 dark:bg-gray-800 dark:border-gray-700'
                          : 'bg-gray-50 border-gray-200 opacity-50 dark:bg-gray-800/50 dark:border-gray-700',
                      ].join(' ')}
                    >
                      <span className={[
                        'relative inline-flex h-5 w-9 items-center rounded-full transition-colors shrink-0',
                        activa ? 'bg-blue-500' : 'bg-gray-300 dark:bg-gray-600',
                      ].join(' ')}>
                        <span className={[
                          'inline-block h-3.5 w-3.5 transform rounded-full bg-white shadow transition-transform',
                          activa ? 'translate-x-4.5' : 'translate-x-0.5',
                        ].join(' ')} />
                      </span>
                      <span className="flex-1 font-mono text-sm text-gray-800 dark:text-gray-200 truncate">
                        {r.patron}
                      </span>
                      <span className="text-xs text-gray-400 dark:text-gray-500 shrink-0">
                        {r.origen === 'SISTEMA' ? 'Sistema' : 'Global'}
                      </span>
                    </div>
                  )
                })
              )}
            </section>
          </div>
        ) : (
          /* ── Modo global ──────────────────────────────────────────────── */
          <div className="p-3 flex flex-col gap-2">
            <FormularioRegla onAgregar={agregarGlobal} />
            {error && <p className="text-sm text-red-600 dark:text-red-400 px-1">{error}</p>}
            {reglasGlobal.length === 0 ? (
              <EstadoVacio
                titulo="Sin reglas"
                descripcion="No hay reglas de exclusión globales definidas."
              />
            ) : (
              reglasGlobal.map(r => (
                <FilaRegla key={r.id} regla={r} onToggle={toggleGlobal} onEliminar={eliminarGlobal} />
              ))
            )}
          </div>
        )}
      </div>
    </div>
  )
}
