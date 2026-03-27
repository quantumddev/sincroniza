# Modelos de datos — Sincroniza

Este documento define todos los modelos de datos del backend como referencia
para la implementación. Cada modelo se implementará como una `dataclass` de
Python con type hints completos.

---

## Enums

### EstadoNodo
Clasifica el estado de cada elemento en el árbol de diferencias.

| Valor | Descripción |
|-------|-------------|
| `NUEVO` | Existe en origen pero no en destino |
| `MODIFICADO` | Existe en ambos pero difiere |
| `ELIMINADO` | Existe en destino pero no en origen |
| `IDENTICO` | Existe en ambos y es igual |
| `EXCLUIDO` | Coincide con una regla de exclusión activa |
| `ERROR` | No se pudo procesar |
| `OMITIDO` | Omitido por regla de seguridad |
| `CONFLICTO_NUBE` | Archivo con patrón de conflicto en destino |

### MetodoComparacion
| Valor | Descripción |
|-------|-------------|
| `TAMAÑO_FECHA` | Compara tamaño + fecha de modificación |
| `HASH` | Compara hash SHA-256 |

### TipoRegla
| Valor | Descripción |
|-------|-------------|
| `ARCHIVO` | La regla aplica solo a archivos |
| `CARPETA` | La regla aplica solo a carpetas |
| `AMBOS` | La regla aplica a archivos y carpetas |

### OrigenRegla
| Valor | Descripción |
|-------|-------------|
| `SISTEMA` | Regla predefinida por la app |
| `USUARIO` | Regla creada por el usuario |

### NivelLog
| Valor | Descripción |
|-------|-------------|
| `INFO` | Información normal |
| `WARNING` | Advertencia |
| `ERROR` | Error |

### EstadoEjecucion
| Valor | Descripción |
|-------|-------------|
| `COMPLETADO` | Terminó correctamente |
| `COMPLETADO_CON_ERRORES` | Terminó pero hay errores recuperables |
| `CANCELADO` | El usuario canceló la operación |
| `FALLIDO` | Error bloqueante impidió continuar |

### TipoOperacion
| Valor | Descripción |
|-------|-------------|
| `COPIAR` | Copiar archivo nuevo |
| `REEMPLAZAR` | Reemplazar archivo modificado |
| `ELIMINAR_ARCHIVO` | Eliminar archivo del destino |
| `ELIMINAR_CARPETA` | Eliminar carpeta del destino |
| `CREAR_CARPETA` | Crear carpeta nueva en destino |

### TipoElemento
| Valor | Descripción |
|-------|-------------|
| `ARCHIVO` | Archivo regular |
| `CARPETA` | Directorio |
| `SYMLINK` | Enlace simbólico |
| `OTRO` | Junction, acceso directo, etc. |

---

## Modelos principales

### Regla

```python
@dataclass(frozen=True)
class Regla:
    id: str                   # UUID v4
    patron: str               # Glob pattern (ej: "node_modules/**")
    tipo: TipoRegla           # archivo, carpeta o ambos
    activa: bool              # Si la regla está habilitada
    origen: OrigenRegla       # sistema o usuario
```

### Perfil

```python
@dataclass
class Perfil:
    id: str                   # UUID v4
    nombre: str               # Nombre descriptivo
    origen: str               # Ruta absoluta del directorio origen
    destino: str              # Ruta absoluta del directorio destino
    metodo_comparacion: MetodoComparacion
    reglas_exclusion_ids: list[str]   # IDs de reglas globales a usar
    reglas_propias: list[Regla]       # Reglas adicionales del perfil
    umbral_eliminaciones: int         # Máximo de eliminaciones sin advertencia
    timeout_por_archivo: int          # Segundos máximo por operación
    creado: str                       # ISO 8601
    ultima_ejecucion: str | None      # ISO 8601 o None
```

### EntradaFilesystem

Representa un elemento detectado al explorar un directorio.

```python
@dataclass(frozen=True)
class EntradaFilesystem:
    ruta_relativa: str        # Ruta relativa al directorio raíz
    tipo: TipoElemento        # archivo, carpeta, symlink, otro
    tamaño: int               # Bytes (0 para carpetas)
    mtime: float              # Timestamp de última modificación
    es_oculto: bool           # Archivo/carpeta oculto del sistema
    es_symlink: bool          # Es enlace simbólico o junction
```

### NodoArbol

Nodo jerárquico del árbol de diferencias.

```python
@dataclass
class NodoArbol:
    nombre: str               # Nombre del archivo o carpeta
    ruta_relativa: str        # Ruta relativa completa
    tipo: TipoElemento        # archivo, carpeta, etc.
    estado: EstadoNodo         # nuevo, modificado, eliminado, etc.
    tamaño: int               # Bytes
    tamaño_destino: int | None # Bytes en destino (si aplica)
    motivo: str | None         # Motivo de exclusión, error o conflicto
    hijos: list['NodoArbol']   # Subnodos (vacío para archivos)
```

### OperacionPlanificada

Una operación concreta que el sincronizador ejecutará.

```python
@dataclass(frozen=True)
class OperacionPlanificada:
    tipo: TipoOperacion        # copiar, reemplazar, eliminar, etc.
    ruta_origen: str | None    # Ruta absoluta en origen (None para eliminaciones)
    ruta_destino: str          # Ruta absoluta en destino
    ruta_relativa: str         # Ruta relativa para UI
    tamaño: int                # Bytes involucrados
```

### ResumenPlan

Resumen numérico del plan de sincronización.

```python
@dataclass(frozen=True)
class ResumenPlan:
    nuevos: int
    modificados: int
    eliminados: int
    identicos: int
    excluidos: int
    errores: int
    conflictos_nube: int
    omitidos: int
    tamaño_copiar: int         # Bytes a copiar (nuevos)
    tamaño_reemplazar: int     # Bytes a reemplazar (modificados)
    tamaño_eliminar: int       # Bytes a eliminar
    total_elementos: int       # Total de elementos analizados
```

### PlanSincronizacion

Resultado completo de un análisis.

```python
@dataclass
class PlanSincronizacion:
    id: str                    # UUID v4
    perfil_id: str             # ID del perfil usado
    origen: str                # Ruta origen analizada
    destino: str               # Ruta destino analizada
    metodo_comparacion: MetodoComparacion
    reglas_activas: list[str]  # IDs de reglas aplicadas
    arbol: NodoArbol           # Árbol jerárquico de diferencias
    operaciones: list[OperacionPlanificada]
    resumen: ResumenPlan
    fingerprint: str           # Hash del plan para detección de desfase
    mtime_origen: float        # mtime del directorio raíz origen al analizar
    mtime_destino: float       # mtime del directorio raíz destino al analizar
    timestamp: str             # ISO 8601 del momento del análisis
```

### ErrorSincronizacion

```python
@dataclass(frozen=True)
class ErrorSincronizacion:
    codigo: str                # Código de error (ej: "PERMISO_DENEGADO")
    mensaje: str               # Descripción legible
    ruta: str                  # Ruta afectada
    fase: str                  # "analisis" o "ejecucion"
    recuperable: bool          # Si se puede reintentar
    timestamp: str             # ISO 8601
```

### ResultadoEjecucion

Resultado persistido de una sincronización ejecutada.

```python
@dataclass
class ResultadoEjecucion:
    id: str                             # UUID v4
    plan_id: str                        # ID del plan que se ejecutó
    perfil_id: str                      # ID del perfil
    origen: str                         # Ruta origen
    destino: str                        # Ruta destino
    metodo_comparacion: MetodoComparacion
    reglas_activas: list[str]           # IDs de reglas aplicadas
    estado: EstadoEjecucion             # completado, cancelado, fallido, etc.
    modo_prueba: bool                   # Si fue modo prueba
    resumen: ResumenPlan                # Resumen numérico
    operaciones_completadas: list[OperacionPlanificada]
    operaciones_fallidas: list[OperacionPlanificada]
    errores: list[ErrorSincronizacion]
    reintentos: list[dict]              # Registro de reintentos realizados
    duracion_analisis: float            # Segundos que duró el análisis
    duracion_ejecucion: float           # Segundos que duró la ejecución
    timestamp_inicio: str               # ISO 8601
    timestamp_fin: str                  # ISO 8601
    version_esquema: int                # Versión del formato JSON
```

### EventoLog

```python
@dataclass(frozen=True)
class EventoLog:
    tipo: str                  # Tipo de evento (ver catálogo en 04_protocolo_jsonrpc.md)
    nivel: NivelLog            # info, warning, error
    mensaje: str               # Texto legible
    datos: dict | None         # Datos estructurados adicionales
    timestamp: str             # ISO 8601
```

### ConfiguracionApp

Refleja el contenido completo de `data/settings.json`.

```python
@dataclass
class ConfiguracionApp:
    version_esquema: int
    tema: str                           # "claro" o "oscuro"
    metodo_comparacion_defecto: MetodoComparacion
    ultimas_rutas: dict                 # {"origen": str|None, "destino": str|None}
    perfiles: list[Perfil]
    reglas_exclusion: list[Regla]
    restricciones_ruta: dict            # {"origen_permitido": list[str], "destino_permitido": list[str]}
    umbral_eliminaciones: int
    timeout_por_archivo: int
    limite_historial: int
```

### PendingSync

Archivo temporal que indica una sincronización interrumpida.

```python
@dataclass
class PendingSync:
    plan_id: str
    perfil_id: str
    timestamp_inicio: str               # ISO 8601
    operaciones_completadas: list[str]  # Rutas relativas ya procesadas
    operaciones_pendientes: list[str]   # Rutas relativas por procesar
```

---

## Serialización

Todos los modelos deben implementar:

- `to_dict() -> dict` — convierte la instancia a diccionario serializable a JSON.
- `@classmethod from_dict(cls, data: dict) -> Self` — reconstruye la instancia
  desde un diccionario.

Los Enums se serializan como strings (`enum.value`) y se reconstruyen con
`Enum(value)`.

Los campos `NodoArbol.hijos` se serializan recursivamente.

---

## Diagrama de relaciones

```
ConfiguracionApp
  ├── Perfil[] ──────────────────┐
  │     ├── Regla[] (propias)    │
  │     └── reglas_exclusion_ids │
  └── Regla[] (globales) ◄──────┘

PlanSincronizacion
  ├── NodoArbol (jerárquico)
  │     └── NodoArbol[] (hijos recursivos)
  ├── OperacionPlanificada[]
  └── ResumenPlan

ResultadoEjecucion
  ├── OperacionPlanificada[] (completadas)
  ├── OperacionPlanificada[] (fallidas)
  ├── ErrorSincronizacion[]
  └── ResumenPlan

PendingSync
  └── referencias a PlanSincronizacion por id
```
