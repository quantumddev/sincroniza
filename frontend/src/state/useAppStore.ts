/**
 * Store principal de la aplicación (Zustand).
 *
 * Contiene todo el estado de dominio: perfiles, plan actual, historial,
 * estado de operaciones, filtros del árbol y crash recovery.
 *
 * Ref: §03_arquitectura_frontend.md — useAppStore
 */

import { create } from 'zustand'
import type {
  EstadoAnalisis,
  EstadoNodo,
  EstadoSync,
  NodoArbolDatos,
  Perfil,
  PlanSincronizacion,
  Regla,
  ResumenHistorial,
  ResultadoEjecucion,
} from '@/lib/tipos'
import { llamarRpc } from '@/lib/rpc'
import {
  EVENTO_ANALISIS_COMPLETADO,
  EVENTO_ANALISIS_ERROR,
  EVENTO_ANALISIS_INICIADO,
  EVENTO_PROGRESO_SYNC,
  EVENTO_SYNC_CANCELADA,
  EVENTO_SYNC_COMPLETADA,
  EVENTO_SYNC_ERROR,
  EVENTO_SYNC_INICIADA,
  extraerPlanDelEvento,
} from '@/lib/eventos'

// ── Estado ────────────────────────────────────────────────────────────────────

interface AppState {
  // Perfiles
  perfiles: Perfil[]
  perfilActivo: Perfil | null

  // Análisis
  planActual: PlanSincronizacion | null
  estadoAnalisis: EstadoAnalisis

  // Sincronización
  estadoSync: EstadoSync
  progresoSync: { completadas: number; total: number } | null
  ultimoResultado: ResultadoEjecucion | null

  // Reglas globales
  reglasGlobales: Regla[]

  // Historial
  historial: ResumenHistorial[]
  totalHistorial: number

  // UI — árbol de diferencias
  filtrosArbol: EstadoNodo[]
  busquedaArbol: string
  nodosExpandidos: Set<string>

  // UI — vistas
  vistaActual: 'principal' | 'historial' | 'reglas' | 'perfiles'

  // Crash recovery
  pendingSyncDetectado: boolean

  // Progreso de análisis (mensaje más reciente)
  mensajeProgreso: string
}

// ── Acciones ──────────────────────────────────────────────────────────────────

interface AppActions {
  // Perfiles
  cargarPerfiles: () => Promise<void>
  setPerfilActivo: (perfil: Perfil | null) => void
  actualizarPerfil: (perfil: Perfil) => void
  eliminarPerfilLocal: (id: string) => void

  // Reglas
  cargarReglas: () => Promise<void>

  // Análisis
  iniciarAnalisis: (perfilId: string) => Promise<void>
  cancelarAnalisis: () => Promise<void>

  // Sincronización
  iniciarSync: (planId: string, modoPrueba?: boolean) => Promise<void>
  cancelarSync: () => Promise<void>

  // Árbol
  toggleFiltroArbol: (estado: EstadoNodo) => void
  setBusquedaArbol: (q: string) => void
  toggleNodoExpandido: (rutaRelativa: string) => void
  expandirTodos: () => void
  colapsarTodos: () => void

  // Historial
  cargarHistorial: (pagina?: number, limite?: number) => Promise<void>

  // Evento push routing
  procesarEvento: (tipo: string, datos: unknown) => void

  // Vista
  setVista: (vista: AppState['vistaActual']) => void,

  // Crash recovery
  setPendingSyncDetectado: (v: boolean) => void
}

type AppStore = AppState & AppActions

// ── Store ──────────────────────────────────────────────────────────────────────

export const useAppStore = create<AppStore>((set, get) => ({
  // ── Estado inicial ──────────────────────────────────────────────────────────
  perfiles: [],
  perfilActivo: null,
  planActual: null,
  estadoAnalisis: 'inactivo',
  estadoSync: 'inactivo',
  progresoSync: null,
  ultimoResultado: null,
  reglasGlobales: [],
  historial: [],
  totalHistorial: 0,
  filtrosArbol: [],
  busquedaArbol: '',
  nodosExpandidos: new Set(),
  vistaActual: 'principal',
  pendingSyncDetectado: false,
  mensajeProgreso: '',

  // ── Perfiles ────────────────────────────────────────────────────────────────

  cargarPerfiles: async () => {
    const perfiles = await llamarRpc<Perfil[]>('perfil.listar')
    set({ perfiles })
    const { perfilActivo } = get()
    if (perfilActivo) {
      const actualizado = perfiles.find(p => p.id === perfilActivo.id)
      set({ perfilActivo: actualizado ?? (perfiles[0] ?? null) })
    } else if (perfiles.length > 0) {
      set({ perfilActivo: perfiles[0] })
    }
  },

  setPerfilActivo: (perfil) => {
    set({
      perfilActivo: perfil,
      planActual: null,
      estadoAnalisis: 'inactivo',
      estadoSync: 'inactivo',
      progresoSync: null,
    })
  },

  actualizarPerfil: (perfil) => {
    set(state => ({
      perfiles: state.perfiles.map(p => p.id === perfil.id ? perfil : p),
      perfilActivo: state.perfilActivo?.id === perfil.id ? perfil : state.perfilActivo,
    }))
  },

  eliminarPerfilLocal: (id) => {
    set(state => {
      const perfiles = state.perfiles.filter(p => p.id !== id)
      const perfilActivo = state.perfilActivo?.id === id
        ? (perfiles[0] ?? null)
        : state.perfilActivo
      return { perfiles, perfilActivo }
    })
  },

  // ── Reglas ──────────────────────────────────────────────────────────────────

  cargarReglas: async () => {
    const reglas = await llamarRpc<Regla[]>('reglas.listar')
    set({ reglasGlobales: reglas })
  },

  // ── Análisis ────────────────────────────────────────────────────────────────

  iniciarAnalisis: async (perfilId) => {
    set({ estadoAnalisis: 'analizando', planActual: null, mensajeProgreso: '' })
    await llamarRpc('analisis.ejecutar', { perfil_id: perfilId })
  },

  cancelarAnalisis: async () => {
    await llamarRpc('analisis.cancelar')
  },

  // ── Sincronización ──────────────────────────────────────────────────────────

  iniciarSync: async (planId, modoPrueba = false) => {
    set({ estadoSync: 'ejecutando', progresoSync: null })
    await llamarRpc('sync.ejecutar', { plan_id: planId, modo_prueba: modoPrueba })
  },

  cancelarSync: async () => {
    await llamarRpc('sync.cancelar')
  },

  // ── Árbol ───────────────────────────────────────────────────────────────────

  toggleFiltroArbol: (estado) => {
    set(state => {
      const activos = state.filtrosArbol.includes(estado)
        ? state.filtrosArbol.filter(e => e !== estado)
        : [...state.filtrosArbol, estado]
      return { filtrosArbol: activos }
    })
  },

  setBusquedaArbol: (q) => set({ busquedaArbol: q }),

  toggleNodoExpandido: (ruta) => {
    set(state => {
      const nuevo = new Set(state.nodosExpandidos)
      if (nuevo.has(ruta)) nuevo.delete(ruta)
      else nuevo.add(ruta)
      return { nodosExpandidos: nuevo }
    })
  },

  expandirTodos: () => {
    const { planActual } = get()
    if (!planActual) return
    const rutas = new Set<string>()
    const recoger = (nodo: { ruta_relativa: string; hijos?: NodoArbolDatos[] }) => {
      if (nodo.hijos && nodo.hijos.length > 0) {
        rutas.add(nodo.ruta_relativa)
        nodo.hijos.forEach(h => recoger(h))
      }
    }
    recoger(planActual.arbol)
    set({ nodosExpandidos: rutas })
  },

  colapsarTodos: () => set({ nodosExpandidos: new Set() }),

  // ── Historial ───────────────────────────────────────────────────────────────

  cargarHistorial: async (pagina = 1, limite = 20) => {
    const r = await llamarRpc<{ items: ResumenHistorial[]; total: number }>(
      'historial.listar',
      { pagina, limite },
    )
    set({ historial: r.items, totalHistorial: r.total })
  },

  // ── Enrutamiento de eventos push ────────────────────────────────────────────

  procesarEvento: (tipo, datos) => {
    switch (tipo) {
      case EVENTO_ANALISIS_INICIADO:
        set({ estadoAnalisis: 'analizando', mensajeProgreso: 'Análisis en curso…' })
        break

      case EVENTO_ANALISIS_COMPLETADO: {
        const plan = extraerPlanDelEvento(datos)
        set({
          estadoAnalisis: 'completado',
          planActual: plan,
          mensajeProgreso: '',
          nodosExpandidos: new Set(),
        })
        break
      }

      case EVENTO_ANALISIS_ERROR:
        set({ estadoAnalisis: 'error', mensajeProgreso: '' })
        break

      case EVENTO_SYNC_INICIADA:
        set({ estadoSync: 'ejecutando' })
        break

      case EVENTO_SYNC_COMPLETADA: {
        const resultado = datos as ResultadoEjecucion | null
        set({ estadoSync: 'completado', ultimoResultado: resultado })
        break
      }

      case EVENTO_SYNC_CANCELADA:
        set({ estadoSync: 'cancelado' })
        break

      case EVENTO_SYNC_ERROR:
        set({ estadoSync: 'error' })
        break

      case EVENTO_PROGRESO_SYNC: {
        const d = datos as { completadas: number; total: number } | null
        if (d) set({ progresoSync: d })
        break
      }

      default:
        // Otros eventos (progreso_analisis, advertencias, etc.) se procesan
        // solo para el log, no afectan el store principal.
        if (tipo === 'progreso_analisis') {
          const d = datos as { procesados?: number; estimado_total?: number } | null
          if (d?.procesados !== undefined) {
            set({ mensajeProgreso: `Procesados ${d.procesados.toLocaleString('es-ES')} elementos…` })
          }
        }
        break
    }
  },

  // ── Vista ───────────────────────────────────────────────────────────────────

  setVista: (vista) => set({ vistaActual: vista }),

  // ── Crash recovery ──────────────────────────────────────────────────────────

  setPendingSyncDetectado: (v) => set({ pendingSyncDetectado: v }),
}))
