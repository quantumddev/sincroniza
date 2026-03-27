import { describe, it, expect, beforeEach } from 'vitest'
import { useTemaStore } from '@/state/useTemaStore'

describe('useTemaStore', () => {
  beforeEach(() => {
    // Resetear localStorage y html class
    localStorage.removeItem('sincroniza-tema')
    document.documentElement.classList.remove('dark')
    // Forzar tema a claro para cada test
    useTemaStore.getState().establecer('claro')
  })

  it('inicia con un tema (claro u oscuro)', () => {
    const { tema } = useTemaStore.getState()
    expect(['claro', 'oscuro']).toContain(tema)
  })

  it('alterna entre claro y oscuro', () => {
    useTemaStore.getState().establecer('claro')
    useTemaStore.getState().alternar()
    expect(useTemaStore.getState().tema).toBe('oscuro')
    useTemaStore.getState().alternar()
    expect(useTemaStore.getState().tema).toBe('claro')
  })

  it('establece el tema directamente', () => {
    useTemaStore.getState().establecer('oscuro')
    expect(useTemaStore.getState().tema).toBe('oscuro')
    useTemaStore.getState().establecer('claro')
    expect(useTemaStore.getState().tema).toBe('claro')
  })

  it('persiste el tema en localStorage', () => {
    useTemaStore.getState().establecer('oscuro')
    expect(localStorage.getItem('sincroniza-tema')).toBe('oscuro')
    useTemaStore.getState().establecer('claro')
    expect(localStorage.getItem('sincroniza-tema')).toBe('claro')
  })

  it('aplica la clase dark al documentElement cuando el tema es oscuro', () => {
    useTemaStore.getState().establecer('oscuro')
    expect(document.documentElement.classList.contains('dark')).toBe(true)
    useTemaStore.getState().establecer('claro')
    expect(document.documentElement.classList.contains('dark')).toBe(false)
  })
})
