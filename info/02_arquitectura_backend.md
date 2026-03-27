# Arquitectura del backend — Sincroniza

---

## Visión general

El backend es una aplicación Python que gestiona toda la lógica de negocio:
exploración del filesystem, comparación de árboles, sincronización espejo,
persistencia y comunicación con el frontend mediante JSON-RPC 2.0 a través de
pywebview.

No expone un servidor HTTP. La comunicación se realiza in-process a través del
bridge de pywebview.

---

## Principios de diseño

1. **Tipado estricto** — dataclasses, Enums y type hints en todas las firmas públicas.
2. **Inyección de dependencias** — cada servicio recibe sus dependencias por constructor; nunca importa singletons globales.
3. **Separación de capas** — modelos → core → storage → services → api → main.
4. **Inmutabilidad cuando sea posible** — los modelos de datos son dataclasses `frozen=True` salvo necesidad justificada.
5. **Hilos para operaciones largas** — análisis y sincronización se ejecutan en `threading.Thread` para no bloquear pywebview.

---

## Estructura de paquetes

```
backend/
├── main.py                     # Entrypoint: crea ventana pywebview e inyecta la API
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dispatcher.py       # Clase Dispatcher JSON-RPC 2.0
│   │   ├── registro.py         # Registra métodos en el dispatcher
│   │   └── eventos.py          # Push de eventos hacia el frontend
│   ├── models/
│   │   ├── __init__.py
│   │   ├── enums.py            # EstadoNodo, MetodoComparacion, TipoRegla, etc.
│   │   ├── regla.py            # Dataclass Regla
│   │   ├── perfil.py           # Dataclass Perfil
│   │   ├── nodo_arbol.py       # Dataclass NodoArbol
│   │   ├── plan.py             # PlanSincronizacion, OperacionPlanificada, ResumenPlan
│   │   ├── resultado.py        # ResultadoEjecucion
│   │   ├── error.py            # ErrorSincronizacion
│   │   ├── evento_log.py       # EventoLog
│   │   └── configuracion.py    # ConfiguracionApp
│   ├── services/
│   │   ├── __init__.py
│   │   ├── explorador.py       # ExploradorServicio
│   │   ├── comparador.py       # ComparadorServicio
│   │   ├── sincronizador.py    # SincronizadorServicio
│   │   ├── reglas.py           # ReglasServicio
│   │   ├── perfiles.py         # PerfilServicio
│   │   ├── historial.py        # HistorialServicio
│   │   ├── validador.py        # ValidadorServicio
│   │   └── log.py              # LogServicio
│   ├── core/
│   │   ├── __init__.py
│   │   ├── normalizacion.py    # Normalización de rutas Windows
│   │   ├── validaciones.py     # Funciones puras de validación
│   │   ├── hashing.py          # SHA-256 por bloques
│   │   ├── fingerprint.py      # Fingerprint de un plan de análisis
│   │   ├── glob_matcher.py     # Evaluación de globs contra rutas
│   │   └── fechas.py           # Utilidades de fechas y timestamps
│   └── storage/
│       ├── __init__.py
│       ├── config_storage.py   # Lectura/escritura de settings.json
│       ├── historial_storage.py# Lectura/escritura/rotación de historial
│       └── pending_storage.py  # Gestión de pending_sync.json
└── tests/
    ├── __init__.py
    ├── test_models/
    ├── test_core/
    ├── test_storage/
    ├── test_services/
    └── test_api/
```

---

## Clases de servicio — responsabilidades

### ExploradorServicio
- Explorar un directorio raíz de forma recursiva.
- Generar lista plana de entradas con metadatos: ruta relativa, tamaño, mtime,
  tipo (archivo/carpeta), es_oculto, es_symlink.
- Manejar errores de permiso o acceso sin interrumpir la exploración completa.
- Respetar prefijo `\\?\` para rutas largas en Windows.

### ComparadorServicio
- Recibir dos listas de entradas (origen y destino) y las reglas activas.
- Clasificar cada entrada en: nuevo, modificado, eliminado, idéntico, excluido,
  error, omitido.
- Soportar comparación por tamaño+fecha (por defecto) o por hash (opcional).
- Detectar archivos con patrón de conflicto de nube en destino.
- Construir un `NodoArbol` jerárquico y un `ResumenPlan`.
- Calcular fingerprint del plan resultante.

### SincronizadorServicio
- Consumir un `PlanSincronizacion` y ejecutar operaciones de forma ordenada:
  1. Crear carpetas nuevas (profundidad primero).
  2. Copiar archivos nuevos.
  3. Reemplazar archivos modificados (copia temporal + renombrar).
  4. Eliminar archivos sobrantes.
  5. Eliminar carpetas sobrantes (profundidad inversa).
- Gestionar `pending_sync.json` durante la ejecución.
- Respetar flag de cancelación (`threading.Event`).
- Aplicar timeout por operación individual.
- Emitir eventos de progreso tras cada operación.
- Producir un `ResultadoEjecucion` al finalizar.

### ReglasServicio
- CRUD de reglas de exclusión.
- Evaluar una ruta contra la lista de reglas activas.
- Diferenciar reglas de sistema (no eliminables) y de usuario.
- Validar sintaxis de patrón glob antes de guardar.

### PerfilServicio
- CRUD de perfiles de sincronización.
- Generar UUID al crear.
- Actualizar `ultima_ejecucion` tras sincronización.
- Delegar persistencia a `ConfigStorage`.

### HistorialServicio
- Guardar `ResultadoEjecucion` como JSON en `data/history/`.
- Listar ejecuciones con paginación.
- Obtener detalle de una ejecución.
- Eliminar registros.
- Aplicar rotación automática al superar el límite.
- Exportar historial completo a archivo.

### ValidadorServicio
- Validar que origen ≠ destino.
- Validar que no hay anidamiento.
- Validar restricciones opcionales de lista blanca.
- Validar que la ruta existe y es accesible.
- Verificar fingerprint antes de ejecutar sincronización.
- Verificar mtime de raíz antes de ejecutar.

### LogServicio
- Acumular eventos en memoria.
- Aceptar un callback (`Callable`) para push en tiempo real.
- Métodos: `info()`, `warning()`, `error()`.
- Generar `EventoLog` con timestamp automático.

---

## Grafo de dependencias entre servicios

```
main.py
  └── Dispatcher
        ├── PerfilServicio ──► ConfigStorage
        ├── ReglasServicio ──► ConfigStorage
        ├── ValidadorServicio ──► ConfigStorage
        ├── ExploradorServicio
        ├── ComparadorServicio ──► ReglasServicio, ExploradorServicio
        ├── SincronizadorServicio ──► PendingStorage, LogServicio
        ├── HistorialServicio ──► HistorialStorage
        ├── LogServicio ──► EventosPush
        └── ConfigStorage
```

---

## Gestión de hilos

```
┌─────────────────────────────────┐
│  Hilo principal (pywebview UI)  │
│                                 │
│  Dispatcher recibe JSON-RPC     │
│  Métodos rápidos → respuesta    │
│  inmediata                      │
│                                 │
│  analisis.ejecutar ──┐          │
│  sync.ejecutar ──────┤          │
│                      ▼          │
│            ┌─────────────┐      │
│            │ Hilo worker │      │
│            │             │      │
│            │ Ejecuta la  │      │
│            │ operación   │◄───── cancelación vía threading.Event
│            │             │
│            │ Push eventos│─────► window.evaluate_js()
│            └─────────────┘
└─────────────────────────────────┘
```

- Solo un hilo worker activo a la vez (bloqueo de concurrencia).
- El dispatcher rechaza `analisis.ejecutar` o `sync.ejecutar` si ya hay un
  worker en curso.
- La cancelación establece un `threading.Event` que el worker revisa antes de
  cada operación.

---

## Estrategia de escritura segura

Para reemplazar archivos modificados:

1. Copiar archivo origen a `destino.tmp_sincroniza`.
2. Si la copia se completa, renombrar `destino.tmp_sincroniza` → archivo final
   (operación atómica en el mismo volumen).
3. Si falla, eliminar `destino.tmp_sincroniza` y registrar error recuperable.

Esto minimiza el riesgo de corrupción si el proceso se interrumpe.

---

## Configuración por defecto

Al arrancar por primera vez, si no existe `data/settings.json`, se genera con:

```json
{
  "version_esquema": 1,
  "tema": "oscuro",
  "metodo_comparacion_defecto": "tamaño_fecha",
  "ultimas_rutas": {
    "origen": null,
    "destino": null
  },
  "perfiles": [],
  "reglas_exclusion": [
    { "id": "sys-01", "patron": "node_modules/**", "tipo": "carpeta", "activa": true, "origen": "sistema" },
    { "id": "sys-02", "patron": ".git/**", "tipo": "carpeta", "activa": true, "origen": "sistema" }
  ],
  "restricciones_ruta": {
    "origen_permitido": [],
    "destino_permitido": []
  },
  "umbral_eliminaciones": 50,
  "timeout_por_archivo": 60,
  "limite_historial": 100
}
```

(La lista completa de reglas de sistema incluye todas las definidas en §10 de la especificación.)
