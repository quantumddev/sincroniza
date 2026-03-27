import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { BotonAccion } from '@/components/BotonAccion'

describe('BotonAccion', () => {
  it('renderiza con texto', () => {
    render(<BotonAccion>Guardar</BotonAccion>)
    expect(screen.getByRole('button', { name: 'Guardar' })).toBeDefined()
  })

  it('renderiza con variante primario por defecto', () => {
    render(<BotonAccion>Test</BotonAccion>)
    const btn = screen.getByRole('button')
    expect(btn.className).toContain('bg-blue-600')
  })

  it('renderiza con variante secundario', () => {
    render(<BotonAccion variante="secundario">Test</BotonAccion>)
    const btn = screen.getByRole('button')
    expect(btn.className).toContain('bg-gray-100')
  })

  it('renderiza con variante peligro', () => {
    render(<BotonAccion variante="peligro">Eliminar</BotonAccion>)
    const btn = screen.getByRole('button')
    expect(btn.className).toContain('bg-red-600')
  })

  it('renderiza con variante fantasma', () => {
    render(<BotonAccion variante="fantasma">Test</BotonAccion>)
    const btn = screen.getByRole('button')
    expect(btn.className).toContain('bg-transparent')
  })

  it('está deshabilitado cuando disabled=true', () => {
    render(<BotonAccion disabled>Test</BotonAccion>)
    const btn = screen.getByRole('button')
    expect(btn).toHaveAttribute('disabled')
  })

  it('está deshabilitado cuando cargando=true', () => {
    render(<BotonAccion cargando>Test</BotonAccion>)
    const btn = screen.getByRole('button')
    expect(btn).toHaveAttribute('disabled')
  })

  it('muestra spinner cuando cargando=true', () => {
    const { container } = render(<BotonAccion cargando>Test</BotonAccion>)
    const spinner = container.querySelector('svg.animate-spin')
    expect(spinner).not.toBeNull()
  })

  it('llama onClick cuando se hace clic', () => {
    const onClick = vi.fn()
    render(<BotonAccion onClick={onClick}>Clic</BotonAccion>)
    fireEvent.click(screen.getByRole('button'))
    expect(onClick).toHaveBeenCalledTimes(1)
  })

  it('no llama onClick si está deshabilitado', () => {
    const onClick = vi.fn()
    render(<BotonAccion onClick={onClick} disabled>Clic</BotonAccion>)
    fireEvent.click(screen.getByRole('button'))
    expect(onClick).not.toHaveBeenCalled()
  })
})
