/**
 * Store de eventos de log (Zustand).
 * Acumula los EventoLog recibidos por push del backend.
 *
 * Ref: §03_arquitectura_frontend.md — useLogStore
 */

import { create } from 'zustand'
import type { EventoLog } from '@/lib/tipos'

const MAX_EVENTOS = 500

interface LogState {
  eventos: EventoLog[]
  agregar: (evento: EventoLog) => void
  limpiar: () => void
}

export const useLogStore = create<LogState>(set => ({
  eventos: [],

  agregar: (evento) =>
    set(state => {
      const eventos = [...state.eventos, evento]
      // Mantener un máximo de MAX_EVENTOS para no acumular memoria
      return { eventos: eventos.length > MAX_EVENTOS ? eventos.slice(-MAX_EVENTOS) : eventos }
    }),

  limpiar: () => set({ eventos: [] }),
}))
