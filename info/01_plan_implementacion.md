# Plan de implementación — Sincroniza V1

Este documento define las fases, tareas y orden de construcción para implementar
la aplicación completa. Cada fase produce un resultado verificable antes de
avanzar a la siguiente.

---

## Convenciones

- Cada fase se marca como completada solo cuando todas sus tareas están hechas y
  verificadas.
- Las fases son secuenciales salvo que se indique lo contrario.
- Las tareas dentro de una fase pueden paralelizarse si son independientes.
- Se referencia la especificación funcional (`idea_inicial.md`) con el símbolo §.

---

## Fase 0 — Preparación del entorno

| # | Tarea | Detalle |
|---|-------|---------|
| 0.1 | Crear estructura de carpetas del backend | `backend/app/{api,models,services,core,storage}`, `main.py`, `__init__.py` en cada paquete |
| 0.2 | Configurar entorno virtual | Verificar `backend/venv` existente o crear uno nuevo. Instalar dependencias base: `pywebview`, `pytest` |
| 0.3 | Crear `backend/requirements.txt` | Lista de dependencias con versiones fijadas |
| 0.4 | Inicializar proyecto frontend | `npm create vite@latest` con React, instalar TailwindCSS v4, crear estructura `src/{components,features,pages,state,lib}` |
| 0.5 | Crear carpeta `data/` y `data/history/` | Con archivos `.gitkeep` para que se incluyan en el repo |
| 0.6 | Configurar `.gitignore` | Excluir `venv/`, `node_modules/`, `dist/`, `__pycache__/`, `data/settings.json`, `data/pending_sync.json`, `data/history/*.json` |
| 0.7 | Verificación | El backend arranca sin error. El frontend compila y sirve una página vacía |

**Resultado:** proyecto scaffolded, listo para codificar.

---

## Fase 1 — Modelos de datos del backend

| # | Tarea | Detalle | Ref |
|---|-------|---------|-----|
| 1.1 | Enums de estado | `EstadoNodo`, `MetodoComparacion`, `TipoRegla`, `OrigenRegla`, `NivelLog`, `EstadoEjecucion`, `FaseOperacion` | §6.1, §10, §15 |
| 1.2 | Modelo `Regla` | Dataclass: id, patron, tipo, activa, origen (sistema/usuario) | §10 |
| 1.3 | Modelo `Perfil` | Dataclass con esquema §13.4 completo | §13.4 |
| 1.4 | Modelo `NodoArbol` | Dataclass: nombre, ruta_relativa, tipo, estado, tamaño, hijos, motivo | §14 |
| 1.5 | Modelo `OperacionPlanificada` | Dataclass: ruta_origen, ruta_destino, tipo_operacion, tamaño | §6.1 |
| 1.6 | Modelo `PlanSincronizacion` | Dataclass: id, timestamp, fingerprint, perfil_id, arbol, operaciones, resumen | §6.1, §6.3 |
| 1.7 | Modelo `ResultadoEjecucion` | Dataclass: id, plan_id, estado, operaciones_completadas, operaciones_fallidas, errores, duracion | §13.3 |
| 1.8 | Modelo `ErrorSincronizacion` | Dataclass: codigo, mensaje, ruta, fase, recuperable, timestamp | §12 |
| 1.9 | Modelo `EventoLog` | Dataclass: tipo, nivel, mensaje, datos, timestamp | §5, §15 |
| 1.10 | Modelo `ResumenPlan` | Dataclass: nuevos, modificados, eliminados, identicos, excluidos, errores, tamaño_copiar, tamaño_reemplazar, tamaño_eliminar | §8 |
| 1.11 | Modelo `ConfiguracionApp` | Dataclass que refleja settings.json completo | §13.2 |
| 1.12 | Tests unitarios de serialización | Cada modelo debe poder serializarse a dict y reconstruirse desde dict | §17 |

**Resultado:** todos los modelos definidos, tipados y con tests de serialización pasando.

---

## Fase 2 — Capa core (utilidades y validaciones)

| # | Tarea | Detalle | Ref |
|---|-------|---------|-----|
| 2.1 | Módulo `normalizacion.py` | Normalizar rutas Windows: barras, case-insensitive, rutas largas (prefijo `\\?\`) | §7 |
| 2.2 | Módulo `validaciones.py` | Funciones: rutas_iguales, ruta_anidada, validar_ruta_existe, validar_restricciones_opcionales | §11 |
| 2.3 | Módulo `hashing.py` | Calcular hash SHA-256 de archivo con lectura por bloques | §7 |
| 2.4 | Módulo `fingerprint.py` | Calcular fingerprint de un plan (hash de origen+destino+reglas+config) | §6.3 |
| 2.5 | Módulo `glob_matcher.py` | Evaluar reglas glob contra rutas, diferenciando archivo/carpeta/ambos | §10 |
| 2.6 | Módulo `fechas.py` | Obtener mtime de archivos/directorios raíz, formatear timestamps ISO 8601 | §6.3 |
| 2.7 | Tests unitarios de core | Cobertura de cada módulo con casos normales y límite | §17 |

**Resultado:** utilidades probadas e independientes de cualquier servicio.

---

## Fase 3 — Capa storage (persistencia)

| # | Tarea | Detalle | Ref |
|---|-------|---------|-----|
| 3.1 | `ConfigStorage` | Leer y escribir `data/settings.json` con versión de esquema. Crear con valores por defecto si no existe | §13.2 |
| 3.2 | `HistorialStorage` | Guardar ejecuciones en `data/history/run_<id>.json`. Listar, obtener, eliminar. Rotación automática al superar el límite | §13.3, §13.5 |
| 3.3 | `PendingSyncStorage` | Crear, leer y eliminar `data/pending_sync.json` | §6.5 |
| 3.4 | Tests de persistencia | Escritura, lectura, rotación, archivo inexistente, JSON corrupto | §17 |

**Resultado:** persistencia funcional con tests. El backend puede leer y escribir configuración e historial.

---

## Fase 4 — Servicios del backend

### 4A — Servicios de soporte

| # | Tarea | Detalle | Ref |
|---|-------|---------|-----|
| 4A.1 | `LogServicio` | Clase que emite `EventoLog` y los acumula en memoria. Acepta un callback para push hacia la UI | §15 |
| 4A.2 | `ValidadorServicio` | Clase que agrupa todas las validaciones de §11. Recibe config como dependencia | §11 |
| 4A.3 | `ReglasServicio` | CRUD de reglas. Evaluar lista de reglas contra una ruta. Diferenciar sistema/usuario. Validar patrón glob | §10 |
| 4A.4 | `PerfilServicio` | CRUD de perfiles. Lectura/escritura delegada a ConfigStorage | §13.4 |
| 4A.5 | Tests de servicios de soporte | Validaciones, reglas, perfiles | §17 |

### 4B — Motor de exploración y comparación

| # | Tarea | Detalle | Ref |
|---|-------|---------|-----|
| 4B.1 | `ExploradorServicio` | Explorar un directorio recursivamente, generar lista plana de archivos/carpetas con metadatos (ruta relativa, tamaño, mtime, tipo). Respetar rutas largas. Marcar ocultos, symlinks | §7 |
| 4B.2 | `ComparadorServicio` | Recibir dos árboles + reglas, producir un `PlanSincronizacion` con árbol de diferencias, operaciones planificadas y resumen. Soportar comparación por tamaño+fecha y por hash | §6.1, §7, §14 |
| 4B.3 | Detección de conflictos nube | Dentro del comparador, detectar patrones de conflicto en destino y marcar como advertencia | §7 |
| 4B.4 | Tests del motor de análisis | Nuevos, modificados, eliminados, idénticos, excluidos, carpetas vacías, symlinks, caracteres especiales, conflictos nube | §17 |

### 4C — Motor de sincronización

| # | Tarea | Detalle | Ref |
|---|-------|---------|-----|
| 4C.1 | `SincronizadorServicio` | Consumir un `PlanSincronizacion` y ejecutar operaciones: copiar, reemplazar (copia temporal + renombrar), eliminar. Emitir eventos de progreso. Soportar cancelación mediante flag. Gestionar pending_sync.json | §6.2, §6.4, §6.5 |
| 4C.2 | Timeout por operación | Implementar timeout configurable por archivo. Marcar como error recuperable si se excede | §7, §12 |
| 4C.3 | Reintento de errores | Método para reintentar operaciones fallidas marcadas como recuperables | §12 |
| 4C.4 | `HistorialServicio` | Crear `ResultadoEjecucion` al finalizar, delegando escritura a `HistorialStorage` | §13.3 |
| 4C.5 | Tests del motor de sincronización | Copia, reemplazo, eliminación, cancelación, crash recovery, idempotencia, timeout | §17 |

**Resultado:** el backend completo puede analizar, sincronizar, cancelar, reintentar y persistir resultados, todo verificado con tests.

---

## Fase 5 — Capa API (JSON-RPC 2.0)

| # | Tarea | Detalle | Ref |
|---|-------|---------|-----|
| 5.1 | `Dispatcher` | Clase que registra métodos, parsea peticiones JSON-RPC, despacha al servicio correcto y devuelve respuesta o error estándar | §5 |
| 5.2 | Registro de métodos | Mapear cada método del catálogo a su servicio: `config.*`, `perfil.*`, `reglas.*`, `validacion.*`, `analisis.*`, `sync.*`, `historial.*`, `sistema.*` | §5 |
| 5.3 | Mecanismo de eventos push | Función que usa `window.evaluate_js()` de pywebview para enviar `EventoLog` al frontend | §5 |
| 5.4 | Ejecución en hilos | Métodos de larga duración (`analisis.ejecutar`, `sync.ejecutar`) deben ejecutarse en un hilo separado. Bloqueo de ejecución concurrente | §16 |
| 5.5 | `main.py` | Entrypoint: crear ventana pywebview, inyectar API, cargar frontend (dev o dist) | §18 |
| 5.6 | Tests de integración del dispatcher | Llamadas JSON-RPC válidas, método no encontrado, parámetros inválidos | §17 |

**Resultado:** el backend es invocable desde el frontend mediante JSON-RPC 2.0. Eventos push funcionan.

---

## Fase 6 — Frontend: infraestructura y layout

| # | Tarea | Detalle | Ref |
|---|-------|---------|-----|
| 6.1 | Cliente JSON-RPC | Módulo `lib/rpc.js`: serializar llamadas, deserializar respuestas, manejar errores | §5 |
| 6.2 | Receptor de eventos push | Callback global `window.__sincroniza_evento` que alimenta un store de logs y progreso | §5 |
| 6.3 | Store global | Zustand o Context para: perfil activo, plan actual, estado de ejecución, logs, tema | §8 |
| 6.4 | Layout principal | Shell de la app: sidebar (perfiles), zona central (configuración + árbol), panel inferior (log). Responsive dentro de la ventana | §8 |
| 6.5 | Tema claro/oscuro | Conmutador con persistencia. Clases TailwindCSS `dark:` | §8 |
| 6.6 | Atajos de teclado | Hook global que captura Ctrl+A, Ctrl+S, Ctrl+F, Ctrl+E, Escape | §8 |

**Resultado:** el frontend arranca, se comunica con el backend, muestra un layout vacío con tema conmutable.

---

## Fase 7 — Frontend: pantallas funcionales

| # | Tarea | Detalle | Ref |
|---|-------|---------|-----|
| 7.1 | Onboarding | Pantalla de bienvenida si no hay perfiles. Guía para crear el primero | §8 |
| 7.2 | Panel de perfiles | Lista de perfiles, crear, editar, eliminar, seleccionar activo | §8, §13.4 |
| 7.3 | Configuración del perfil | Selectores de ruta (llaman a `sistema.seleccionar_directorio`), método de comparación, umbral de eliminaciones | §8 |
| 7.4 | Gestión de reglas | Lista de reglas globales y propias del perfil. Crear, editar, eliminar, activar/desactivar. Indicar tipo y origen | §10 |
| 7.5 | Botones de acción | Analizar, Modo prueba, Sincronizar, Cancelar, Reintentar errores. Estados habilitado/deshabilitado según contexto | §8 |
| 7.6 | Panel de resumen | Totales por categoría + tamaños estimados | §8, §14 |
| 7.7 | Árbol de diferencias | Componente virtualizado con tanstack-virtual o equivalente. Estados con color. Expandir/colapsar. Indicadores agregados | §14 |
| 7.8 | Filtros del árbol | Filtro por estado (nuevo, modificado, eliminado, idéntico, excluido, error). Contador de ocultos | §14 |
| 7.9 | Búsqueda en el árbol | Campo de texto que filtra nodos por nombre o ruta | §14 |
| 7.10 | Panel de log | Lista de eventos con nivel, timestamp y mensaje. Auto-scroll. Niveles diferenciados con color | §15 |
| 7.11 | Historial de ejecuciones | Lista paginada de ejecuciones anteriores. Ver detalle, exportar, eliminar | §13.3, §13.5 |
| 7.12 | Diálogo de confirmación | Modal antes de sincronizar. Destacar eliminaciones. Bloquear si hay desfase | §11 |
| 7.13 | Aviso de crash recovery | Al arrancar, si existe pending_sync.json, mostrar modal informativo | §6.5 |

**Resultado:** la interfaz completa está funcional y conectada al backend.

---

## Fase 8 — Integración y pruebas end-to-end

| # | Tarea | Detalle | Ref |
|---|-------|---------|-----|
| 8.1 | Test E2E: primer uso | App arranca → onboarding → crear perfil → seleccionar rutas → analizar → ver árbol | §9 |
| 8.2 | Test E2E: sincronización completa | Analizar → confirmar → sincronizar → historial registrado | §9 |
| 8.3 | Test E2E: modo prueba | Analizar → modo prueba → no se modifica filesystem → se muestra resultado | §4.1 |
| 8.4 | Test E2E: cancelación | Iniciar sync → cancelar → verificar estado parcial y historial | §6.4 |
| 8.5 | Test E2E: reintento de errores | Provocar errores → reintentar individuales → verificar resultado | §12 |
| 8.6 | Test E2E: desfase | Analizar → modificar origen → intentar sincronizar → debe pedir re-análisis | §6.3 |
| 8.7 | Test E2E: crash recovery | Simular pending_sync.json al arrancar → verificar aviso | §6.5 |
| 8.8 | Test de rendimiento del árbol | Generar estructura de +10.000 nodos → verificar fluidez de scroll y filtros | §16 |
| 8.9 | Revisión de accesibilidad | Contraste, navegación por teclado, estados de foco | §8 |

**Resultado:** la aplicación funciona de extremo a extremo con todos los flujos verificados.

---

## Fase 9 — Pulido y empaquetado

| # | Tarea | Detalle | Ref |
|---|-------|---------|-----|
| 9.1 | Build del frontend | `npm run build` → archivos estáticos en `frontend/dist/` | §18 |
| 9.2 | Integrar dist en pywebview | `main.py` carga `frontend/dist/index.html` en producción | §5 |
| 9.3 | Configurar PyInstaller | Generar ejecutable standalone para Windows | §19 |
| 9.4 | Revisión final de UX | Mensajes, tooltips, estados vacíos, textos en español | §8 |
| 9.5 | Documentación de uso | README actualizado con instrucciones de instalación, desarrollo y uso | — |

**Resultado:** aplicación empaquetada como ejecutable, lista para uso.

---

## Diagrama de dependencias entre fases

```
Fase 0 (Entorno)
  │
  ▼
Fase 1 (Modelos)
  │
  ├──▶ Fase 2 (Core)
  │       │
  │       ▼
  │    Fase 3 (Storage)
  │       │
  │       ▼
  │    Fase 4A (Servicios soporte)
  │       │
  │       ├──▶ Fase 4B (Análisis)
  │       │       │
  │       │       ▼
  │       │    Fase 4C (Sincronización)
  │       │       │
  │       │       ▼
  │       └──▶ Fase 5 (API JSON-RPC)
  │               │
  ▼               ▼
Fase 6 (Frontend infra) ◀── depende de Fase 5
  │
  ▼
Fase 7 (Frontend pantallas)
  │
  ▼
Fase 8 (Integración y E2E)
  │
  ▼
Fase 9 (Pulido y empaquetado)
```

---

## Resumen de entregables por fase

| Fase | Entregable clave |
|------|-----------------|
| 0 | Proyecto scaffolded y arrancable |
| 1 | Modelos tipados con tests de serialización |
| 2 | Utilidades core con tests |
| 3 | Persistencia JSON funcional con tests |
| 4A | Servicios de soporte con tests |
| 4B | Motor de análisis con tests |
| 4C | Motor de sincronización con tests |
| 5 | API JSON-RPC integrada en pywebview |
| 6 | Frontend con layout, tema y comunicación RPC |
| 7 | Todas las pantallas funcionales |
| 8 | Tests E2E pasando |
| 9 | Ejecutable empaquetado |
