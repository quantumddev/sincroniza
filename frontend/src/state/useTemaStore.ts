/**
 * Store de tema visual (Zustand + persistencia en localStorage).
 *
 * Alterna entre 'claro' y 'oscuro'. La clase `.dark` se aplica al elemento
 * `<html>` para activar las variantes TailwindCSS `dark:`.
 *
 * Ref: §03_arquitectura_frontend.md — useTemaStore
 */

import { create } from 'zustand'

export type Tema = 'claro' | 'oscuro'

const STORAGE_KEY = 'sincroniza-tema'

function leerTemaGuardado(): Tema {
  try {
    const guardado = localStorage.getItem(STORAGE_KEY)
    if (guardado === 'claro' || guardado === 'oscuro') return guardado
  } catch {
    // SSR / entornos sin localStorage
  }
  // Fallback al sistema operativo
  if (typeof window !== 'undefined' && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    return 'oscuro'
  }
  return 'claro'
}

function aplicarTema(tema: Tema): void {
  if (typeof document === 'undefined') return
  document.documentElement.classList.toggle('dark', tema === 'oscuro')
  try {
    localStorage.setItem(STORAGE_KEY, tema)
  } catch {
    // ignore
  }
}

interface TemaState {
  tema: Tema
  alternar: () => void
  establecer: (tema: Tema) => void
}

export const useTemaStore = create<TemaState>(set => {
  const temaInicial = leerTemaGuardado()
  aplicarTema(temaInicial)

  return {
    tema: temaInicial,

    alternar: () =>
      set(state => {
        const nuevo: Tema = state.tema === 'claro' ? 'oscuro' : 'claro'
        aplicarTema(nuevo)
        return { tema: nuevo }
      }),

    establecer: (tema) => {
      aplicarTema(tema)
      set({ tema })
    },
  }
})
