import { describe, it, expect, beforeEach } from 'vitest'
import { useLogStore } from '@/state/useLogStore'
import type { EventoLog } from '@/lib/tipos'

const crearEvento = (msg: string = 'test', nivel: EventoLog['nivel'] = 'INFO'): EventoLog => ({
  tipo: 'log',
  nivel,
  mensaje: msg,
  datos: null,
  timestamp: new Date().toISOString(),
})

describe('useLogStore', () => {
  beforeEach(() => {
    useLogStore.getState().limpiar()
  })

  it('inicia con eventos vacíos', () => {
    expect(useLogStore.getState().eventos).toHaveLength(0)
  })

  it('agrega eventos', () => {
    useLogStore.getState().agregar(crearEvento('Primer evento'))
    useLogStore.getState().agregar(crearEvento('Segundo evento'))
    expect(useLogStore.getState().eventos).toHaveLength(2)
    expect(useLogStore.getState().eventos[0].mensaje).toBe('Primer evento')
  })

  it('limpia los eventos', () => {
    useLogStore.getState().agregar(crearEvento())
    useLogStore.getState().limpiar()
    expect(useLogStore.getState().eventos).toHaveLength(0)
  })

  it('no supera MAX_EVENTOS (500)', () => {
    for (let i = 0; i < 520; i++) {
      useLogStore.getState().agregar(crearEvento(`evento ${i}`))
    }
    const { eventos } = useLogStore.getState()
    expect(eventos.length).toBeLessThanOrEqual(500)
    // Los más recientes deben estar al final
    expect(eventos[eventos.length - 1].mensaje).toBe('evento 519')
  })

  it('maneja correctamente distintos niveles', () => {
    useLogStore.getState().agregar(crearEvento('info', 'INFO'))
    useLogStore.getState().agregar(crearEvento('warn', 'WARNING'))
    useLogStore.getState().agregar(crearEvento('err', 'ERROR'))
    const { eventos } = useLogStore.getState()
    expect(eventos[0].nivel).toBe('INFO')
    expect(eventos[1].nivel).toBe('WARNING')
    expect(eventos[2].nivel).toBe('ERROR')
  })
})
