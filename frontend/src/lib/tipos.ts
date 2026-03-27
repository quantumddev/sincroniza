/**
 * Tipos TypeScript compartidos del frontend — espejo de los modelos del backend.
 * Ref: §03_arquitectura_frontend.md, §05_modelos_datos.md
 */

// ── Enumeraciones ─────────────────────────────────────────────────────────────

export type EstadoNodo =
  | 'NUEVO'
  | 'MODIFICADO'
  | 'ELIMINADO'
  | 'IDENTICO'
  | 'EXCLUIDO'
  | 'ERROR'
  | 'OMITIDO'
  | 'CONFLICTO_NUBE'

export type MetodoComparacion = 'TAMAÑO_FECHA' | 'HASH'

export type TipoRegla = 'ARCHIVO' | 'CARPETA' | 'AMBOS'

export type OrigenRegla = 'SISTEMA' | 'USUARIO'

export type NivelLog = 'INFO' | 'WARNING' | 'ERROR'

export type EstadoEjecucion =
  | 'COMPLETADO'
  | 'COMPLETADO_CON_ERRORES'
  | 'CANCELADO'
  | 'FALLIDO'

export type TipoOperacion =
  | 'COPIAR'
  | 'REEMPLAZAR'
  | 'ELIMINAR_ARCHIVO'
  | 'ELIMINAR_CARPETA'
  | 'CREAR_CARPETA'

export type TipoElemento = 'ARCHIVO' | 'CARPETA' | 'SYMLINK' | 'OTRO'

// ── Modelos del dominio ───────────────────────────────────────────────────────

export interface Regla {
  id: string
  patron: string
  tipo: TipoRegla
  activa: boolean
  origen: OrigenRegla
}

export interface Perfil {
  id: string
  nombre: string
  origen: string
  destino: string
  metodo_comparacion: MetodoComparacion
  reglas_exclusion_ids: string[]
  reglas_propias: Regla[]
  umbral_eliminaciones: number
  timeout_por_archivo: number
  creado: string
  ultima_ejecucion: string | null
}

export interface NodoArbolDatos {
  nombre: string
  ruta_relativa: string
  tipo: TipoElemento
  estado: EstadoNodo
  tamaño: number
  tamaño_destino: number | null
  motivo: string | null
  hijos: NodoArbolDatos[]
}

export interface ResumenPlan {
  nuevos: number
  modificados: number
  eliminados: number
  identicos: number
  excluidos: number
  errores: number
  conflictos_nube: number
  omitidos: number
  tamaño_copiar: number
  tamaño_reemplazar: number
  tamaño_eliminar: number
  total_elementos: number
}

export interface OperacionPlanificada {
  tipo: TipoOperacion
  ruta_origen: string | null
  ruta_destino: string
  ruta_relativa: string
  tamaño: number
}

export interface PlanSincronizacion {
  id: string
  perfil_id: string
  origen: string
  destino: string
  metodo_comparacion: MetodoComparacion
  reglas_activas: string[]
  arbol: NodoArbolDatos
  operaciones: OperacionPlanificada[]
  resumen: ResumenPlan
  fingerprint: string
  mtime_origen: number
  mtime_destino: number
  timestamp: string
}

export interface ErrorSincronizacion {
  codigo: string
  mensaje: string
  ruta: string
  fase: string
  recuperable: boolean
  timestamp: string
}

export interface ResultadoEjecucion {
  id: string
  plan_id: string
  perfil_id: string
  origen: string
  destino: string
  metodo_comparacion: MetodoComparacion
  reglas_activas: string[]
  estado: EstadoEjecucion
  modo_prueba: boolean
  resumen: ResumenPlan
  operaciones_completadas: OperacionPlanificada[]
  operaciones_fallidas: OperacionPlanificada[]
  errores: ErrorSincronizacion[]
  reintentos: unknown[]
  duracion_analisis: number
  duracion_ejecucion: number
  timestamp_inicio: string
  timestamp_fin: string
  version_esquema: number
}

export interface EventoLog {
  tipo: string
  nivel: NivelLog
  mensaje: string
  datos: Record<string, unknown> | null
  timestamp: string
}

export interface ConfiguracionApp {
  version_esquema: number
  tema: string
  metodo_comparacion_defecto: MetodoComparacion
  ultimas_rutas: { origen: string | null; destino: string | null }
  perfiles: Perfil[]
  reglas_exclusion: Regla[]
  restricciones_ruta: { origen_permitido: string[]; destino_permitido: string[] }
  umbral_eliminaciones: number
  timeout_por_archivo: number
  limite_historial: number
}

// ── Item de historial (resumen para listado) ──────────────────────────────────

export interface ResumenHistorial {
  id: string
  perfil_id: string
  origen: string
  destino: string
  estado: EstadoEjecucion
  modo_prueba: boolean
  timestamp_inicio: string
  timestamp_fin: string
  duracion_ejecucion: number
  resumen: ResumenPlan
}

// ── Nodo aplanado para virtualización del árbol ───────────────────────────────

export interface NodoAplanado {
  id: string
  nombre: string
  ruta_relativa: string
  tipo: TipoElemento
  estado: EstadoNodo
  tamaño: number
  tamaño_destino: number | null
  motivo: string | null
  nivel: number
  tieneHijos: boolean
  expandido: boolean
}

// ── Estados del ciclo de vida ─────────────────────────────────────────────────

export type EstadoAnalisis = 'inactivo' | 'analizando' | 'completado' | 'error'
export type EstadoSync = 'inactivo' | 'ejecutando' | 'completado' | 'cancelado' | 'error'
