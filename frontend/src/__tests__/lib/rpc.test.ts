import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { llamarRpc, RpcError, ERR_INTERNAL, ERR_METHOD_NOT_FND } from '@/lib/rpc'

describe('RpcError', () => {
  it('crea un error con código y mensaje', () => {
    const err = new RpcError(-32601, 'Método no encontrado')
    expect(err.name).toBe('RpcError')
    expect(err.code).toBe(-32601)
    expect(err.message).toBe('Método no encontrado')
    expect(err instanceof Error).toBe(true)
    expect(err instanceof RpcError).toBe(true)
  })

  it('almacena data opcional', () => {
    const err = new RpcError(-32001, 'Validación', { campo: 'nombre' })
    expect(err.data).toEqual({ campo: 'nombre' })
  })
})

describe('llamarRpc', () => {
  let originalPywebview: Window['pywebview']

  beforeEach(() => {
    originalPywebview = window.pywebview
  })

  afterEach(() => {
    window.pywebview = originalPywebview
  })

  it('lanza RpcError si pywebview no está disponible', async () => {
    window.pywebview = undefined
    await expect(llamarRpc('test.metodo')).rejects.toThrowError(RpcError)
    await expect(llamarRpc('test.metodo')).rejects.toMatchObject({ code: ERR_INTERNAL })
  })

  it('devuelve el resultado en caso de éxito', async () => {
    const mockResult = { nombre: 'Perfil test' }
    window.pywebview = {
      api: {
        despachar: vi.fn().mockResolvedValue(
          JSON.stringify({ jsonrpc: '2.0', id: '1', result: mockResult })
        ),
      },
    }
    const result = await llamarRpc<typeof mockResult>('perfil.obtener', { id: '1' })
    expect(result).toEqual(mockResult)
  })

  it('lanza RpcError cuando el backend devuelve un error', async () => {
    window.pywebview = {
      api: {
        despachar: vi.fn().mockResolvedValue(
          JSON.stringify({
            jsonrpc: '2.0',
            id: '1',
            error: { code: ERR_METHOD_NOT_FND, message: 'Método no encontrado' },
          })
        ),
      },
    }
    await expect(llamarRpc('metodo.inexistente')).rejects.toThrowError(RpcError)
    await expect(llamarRpc('metodo.inexistente')).rejects.toMatchObject({
      code: ERR_METHOD_NOT_FND,
    })
  })

  it('incluye los parámetros en la petición JSON-RPC', async () => {
    const spy = vi.fn().mockResolvedValue(
      JSON.stringify({ jsonrpc: '2.0', id: '1', result: true })
    )
    window.pywebview = { api: { despachar: spy } }

    await llamarRpc('test.metodo', { clave: 'valor' })

    const llamada = JSON.parse(spy.mock.calls[0][0])
    expect(llamada.method).toBe('test.metodo')
    expect(llamada.params).toEqual({ clave: 'valor' })
    expect(llamada.jsonrpc).toBe('2.0')
    expect(llamada.id).toBeTruthy()
  })
})
