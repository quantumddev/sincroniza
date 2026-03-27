import { describe, it, expect } from 'vitest'
import {
  formatearTamano,
  formatearFecha,
  formatearHora,
  formatearDuracion,
  pluralizar,
  ETIQUETAS_ESTADO,
  ETIQUETAS_EJECUCION,
  ETIQUETAS_METODO,
} from '@/lib/formato'

describe('formatearTamano', () => {
  it('formatea bytes', () => {
    expect(formatearTamano(0)).toBe('0 B')
    expect(formatearTamano(500)).toBe('500 B')
  })
  it('formatea kilobytes', () => {
    expect(formatearTamano(1024)).toBe('1.0 KB')
    expect(formatearTamano(2048)).toBe('2.0 KB')
  })
  it('formatea megabytes', () => {
    expect(formatearTamano(1024 * 1024)).toBe('1.0 MB')
  })
  it('formatea gigabytes', () => {
    expect(formatearTamano(1024 * 1024 * 1024)).toBe('1.00 GB')
  })
  it('devuelve 0 B para negativos', () => {
    expect(formatearTamano(-1)).toBe('0 B')
  })
})

describe('formatearFecha', () => {
  it('devuelve — para cadena vacía', () => {
    expect(formatearFecha('')).toBe('—')
  })
  it('formatea una fecha ISO válida', () => {
    const result = formatearFecha('2024-01-15T10:30:00.000Z')
    expect(result).toBeTruthy()
    expect(result).not.toBe('—')
  })
  it('devuelve el input si no es fecha válida', () => {
    expect(formatearFecha('no-es-fecha')).toBe('no-es-fecha')
  })
})

describe('formatearHora', () => {
  it('devuelve — para cadena vacía', () => {
    expect(formatearHora('')).toBe('—')
  })
  it('formatea una hora ISO válida', () => {
    const result = formatearHora('2024-01-15T10:30:45.000Z')
    expect(result).toBeTruthy()
    expect(result.includes(':')).toBe(true)
  })
})

describe('formatearDuracion', () => {
  it('formatea segundos', () => {
    expect(formatearDuracion(45)).toBe('45s')
    expect(formatearDuracion(0)).toBe('0s')
  })
  it('formatea minutos y segundos', () => {
    expect(formatearDuracion(90)).toBe('1m 30s')
    expect(formatearDuracion(3661)).toBe('61m 1s')
  })
  it('devuelve 0s para negativos', () => {
    expect(formatearDuracion(-5)).toBe('0s')
  })
})

describe('pluralizar', () => {
  it('usa singular para 1', () => {
    expect(pluralizar(1, 'archivo', 'archivos')).toBe('archivo')
  })
  it('usa plural para 0 y números > 1', () => {
    expect(pluralizar(0, 'archivo', 'archivos')).toBe('archivos')
    expect(pluralizar(5, 'archivo', 'archivos')).toBe('archivos')
  })
})

describe('ETIQUETAS_ESTADO', () => {
  it('contiene todos los estados', () => {
    expect(ETIQUETAS_ESTADO.NUEVO).toBe('Nuevo')
    expect(ETIQUETAS_ESTADO.MODIFICADO).toBe('Modificado')
    expect(ETIQUETAS_ESTADO.ELIMINADO).toBe('Eliminado')
    expect(ETIQUETAS_ESTADO.IDENTICO).toBe('Idéntico')
    expect(ETIQUETAS_ESTADO.EXCLUIDO).toBe('Excluido')
    expect(ETIQUETAS_ESTADO.ERROR).toBe('Error')
    expect(ETIQUETAS_ESTADO.OMITIDO).toBe('Omitido')
    expect(ETIQUETAS_ESTADO.CONFLICTO_NUBE).toBe('Conflicto')
  })
})

describe('ETIQUETAS_EJECUCION', () => {
  it('contiene todos los estados de ejecución', () => {
    expect(ETIQUETAS_EJECUCION.COMPLETADO).toBe('Completado')
    expect(ETIQUETAS_EJECUCION.COMPLETADO_CON_ERRORES).toBe('Con errores')
    expect(ETIQUETAS_EJECUCION.CANCELADO).toBe('Cancelado')
    expect(ETIQUETAS_EJECUCION.FALLIDO).toBe('Fallido')
  })
})

describe('ETIQUETAS_METODO', () => {
  it('contiene todos los métodos', () => {
    expect(ETIQUETAS_METODO['TAMAÑO_FECHA']).toBeTruthy()
    expect(ETIQUETAS_METODO['HASH']).toBeTruthy()
  })
})
