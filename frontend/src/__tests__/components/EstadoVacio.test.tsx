import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { EstadoVacio } from '@/components/EstadoVacio'

describe('EstadoVacio', () => {
  it('muestra el título', () => {
    render(<EstadoVacio titulo="Sin datos" />)
    expect(screen.getByText('Sin datos')).toBeDefined()
  })

  it('muestra la descripción si se proporciona', () => {
    render(<EstadoVacio titulo="Sin datos" descripcion="No hay elementos disponibles" />)
    expect(screen.getByText('No hay elementos disponibles')).toBeDefined()
  })

  it('no muestra descripción si no se proporciona', () => {
    render(<EstadoVacio titulo="Sin datos" />)
    expect(screen.queryByText('No hay elementos')).toBeNull()
  })

  it('renderiza el icono si se proporciona', () => {
    render(<EstadoVacio titulo="Test" icono={<span data-testid="icono">📁</span>} />)
    expect(screen.getByTestId('icono')).toBeDefined()
  })

  it('no renderiza el icono si no se proporciona', () => {
    const { container } = render(<EstadoVacio titulo="Test" />)
    // No debe haber texto-4xl div si no hay icono
    const iconoDiv = container.querySelector('.text-4xl')
    expect(iconoDiv).toBeNull()
  })

  it('renderiza la acción si se proporciona', () => {
    render(
      <EstadoVacio
        titulo="Sin datos"
        accion={<button>Crear</button>}
      />
    )
    expect(screen.getByRole('button', { name: 'Crear' })).toBeDefined()
  })
})
