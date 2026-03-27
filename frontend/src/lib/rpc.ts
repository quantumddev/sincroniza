/**
 * Cliente JSON-RPC 2.0 para comunicación con el backend vía pywebview bridge.
 *
 * La API pywebview está disponible como `window.pywebview.api.despachar(json)`.
 * En entornos de test o desarrollo sin pywebview, el cliente lanza un error
 * controlado para facilitar el mock.
 *
 * Ref: §03_arquitectura_frontend.md — «Llamadas RPC»
 */

// ── Declaración del bridge pywebview ─────────────────────────────────────────

interface PywebviewApi {
  despachar(json: string): Promise<string>
}

declare global {
  interface Window {
    pywebview?: { api: PywebviewApi }
    __sincroniza_evento?: (eventoJson: string) => void
  }
}

// ── Error de la capa RPC ──────────────────────────────────────────────────────

export class RpcError extends Error {
  readonly code: number
  readonly data: unknown

  constructor(code: number, message: string, data?: unknown) {
    super(message)
    this.name = 'RpcError'
    this.code = code
    this.data = data
  }
}

// ── Códigos de error JSON-RPC 2.0 ────────────────────────────────────────────

export const ERR_PARSE          = -32700
export const ERR_INVALID_REQ    = -32600
export const ERR_METHOD_NOT_FND = -32601
export const ERR_INVALID_PARAMS = -32602
export const ERR_INTERNAL       = -32603

// Códigos de aplicación
export const ERR_VALIDATION     = -32001
export const ERR_OP_IN_PROGRESS = -32002
export const ERR_STALE_PLAN     = -32003
export const ERR_PERFIL_NF      = -32004
export const ERR_REGLA_INVALID  = -32005
export const ERR_HISTORIAL_NF   = -32006
export const ERR_CANCELLED      = -32007
export const ERR_FILESYSTEM     = -32008
export const ERR_TIMEOUT        = -32009

// ── Interfaz JSON-RPC interna ─────────────────────────────────────────────────

interface PeticionRpc {
  jsonrpc: '2.0'
  id: string
  method: string
  params: Record<string, unknown>
}

interface RespuestaRpcOk<T> {
  jsonrpc: '2.0'
  id: string
  result: T
}

interface RespuestaRpcError {
  jsonrpc: '2.0'
  id: string
  error: { code: number; message: string; data?: unknown }
}

type RespuestaRpc<T> = RespuestaRpcOk<T> | RespuestaRpcError

function esRespuestaError<T>(r: RespuestaRpc<T>): r is RespuestaRpcError {
  return 'error' in r
}

// ── Cliente principal ─────────────────────────────────────────────────────────

/**
 * Realiza una llamada JSON-RPC 2.0 al backend.
 *
 * @param metodo  Nombre del método (ej: `"perfil.listar"`)
 * @param params  Parámetros del método
 * @returns       Resultado tipado de la llamada
 * @throws        `RpcError` si el backend devuelve un error JSON-RPC
 */
export async function llamarRpc<T>(
  metodo: string,
  params: Record<string, unknown> = {},
): Promise<T> {
  const peticion: PeticionRpc = {
    jsonrpc: '2.0',
    id: crypto.randomUUID(),
    method: metodo,
    params,
  }

  const bridge = window.pywebview?.api
  if (!bridge) {
    if (import.meta.env.DEV) {
      // En desarrollo sin pywebview simulamos respuestas vacías para que la UI cargue.
      // En producción (pywebview presente) este bloque nunca se ejecuta.
      console.warn(`[RPC dev] Sin pywebview — respondiendo vacío para: ${metodo}`)
      const mock: RespuestaRpcOk<unknown> = { jsonrpc: '2.0', id: peticion.id, result: null }
      return mock.result as T
    }
    throw new RpcError(
      ERR_INTERNAL,
      'pywebview bridge no disponible. ¿El frontend está dentro de pywebview?',
    )
  }

  const respuestaRaw = await bridge.despachar(JSON.stringify(peticion))
  const respuesta = JSON.parse(respuestaRaw) as RespuestaRpc<T>

  if (esRespuestaError(respuesta)) {
    const { code, message, data } = respuesta.error
    throw new RpcError(code, message, data)
  }

  return respuesta.result
}
