# Protocolo de comunicación JSON-RPC 2.0 — Sincroniza

---

## Introducción

La comunicación entre frontend y backend sigue el estándar
[JSON-RPC 2.0](https://www.jsonrpc.org/specification). No se usa HTTP; las
llamadas viajan a través del bridge in-process de pywebview.

---

## Flujo de una llamada

```
Frontend                              Backend
   │                                     │
   │  pywebview.api.ejecutar_rpc(json)   │
   │ ──────────────────────────────────► │
   │                                     │  Dispatcher.despachar(json)
   │                                     │    → parsear petición
   │                                     │    → buscar método registrado
   │                                     │    → ejecutar servicio
   │                                     │    → construir respuesta
   │  ◄────────────────────────────────  │
   │  return json_respuesta              │
   │                                     │
```

---

## Formato de petición

```json
{
  "jsonrpc": "2.0",
  "id": "uuid-del-frontend",
  "method": "perfil.listar",
  "params": {}
}
```

- `id`: string UUID generado por el frontend. Se devuelve en la respuesta para
  correlación.
- `method`: nombre cualificado del método (namespace.accion).
- `params`: objeto con los parámetros del método. Puede omitirse si no hay
  parámetros.

---

## Formato de respuesta exitosa

```json
{
  "jsonrpc": "2.0",
  "id": "uuid-del-frontend",
  "result": { ... }
}
```

---

## Formato de respuesta con error

```json
{
  "jsonrpc": "2.0",
  "id": "uuid-del-frontend",
  "error": {
    "code": -32602,
    "message": "Parámetros inválidos",
    "data": {
      "detalle": "El campo 'origen' es obligatorio"
    }
  }
}
```

---

## Códigos de error

### Códigos estándar JSON-RPC

| Código | Significado |
|--------|------------|
| -32700 | Error de parseo: JSON inválido |
| -32600 | Petición inválida: no cumple estructura JSON-RPC |
| -32601 | Método no encontrado |
| -32602 | Parámetros inválidos |
| -32603 | Error interno del servidor |

### Códigos de aplicación (rango -32000 a -32099)

| Código | Significado |
|--------|------------|
| -32001 | Validación de rutas fallida |
| -32002 | Operación en curso (bloqueo de concurrencia) |
| -32003 | Plan de análisis desactualizado (desfase) |
| -32004 | Perfil no encontrado |
| -32005 | Regla inválida |
| -32006 | Historial no encontrado |
| -32007 | Operación cancelada |
| -32008 | Error de filesystem |
| -32009 | Timeout de operación |

---

## Catálogo de métodos

### config.*

| Método | Params | Resultado | Descripción |
|--------|--------|-----------|-------------|
| `config.obtener` | — | `ConfiguracionApp` | Devuelve la configuración completa |
| `config.guardar` | `{ config: ConfiguracionApp }` | `{ ok: true }` | Persiste la configuración |

### perfil.*

| Método | Params | Resultado | Descripción |
|--------|--------|-----------|-------------|
| `perfil.listar` | — | `Perfil[]` | Lista todos los perfiles |
| `perfil.obtener` | `{ id: string }` | `Perfil` | Obtiene un perfil por id |
| `perfil.crear` | `{ perfil: PerfilNuevo }` | `Perfil` | Crea un perfil y devuelve el objeto con id generado |
| `perfil.actualizar` | `{ id: string, cambios: Partial<Perfil> }` | `Perfil` | Actualiza campos del perfil |
| `perfil.eliminar` | `{ id: string }` | `{ ok: true }` | Elimina un perfil |

### reglas.*

| Método | Params | Resultado | Descripción |
|--------|--------|-----------|-------------|
| `reglas.listar` | — | `Regla[]` | Lista todas las reglas globales |
| `reglas.guardar` | `{ reglas: Regla[] }` | `{ ok: true }` | Persiste el conjunto completo de reglas |

### validacion.*

| Método | Params | Resultado | Descripción |
|--------|--------|-----------|-------------|
| `validacion.verificar_rutas` | `{ origen: string, destino: string }` | `{ valido: bool, errores: string[] }` | Ejecuta todas las validaciones de seguridad sobre las rutas |

### analisis.*

| Método | Params | Resultado | Descripción |
|--------|--------|-----------|-------------|
| `analisis.ejecutar` | `{ perfil_id: string }` | `PlanSincronizacion` | Ejecuta análisis completo. Se ejecuta en hilo separado. Emite eventos de progreso |
| `analisis.cancelar` | — | `{ ok: true }` | Cancela el análisis en curso |

### sync.*

| Método | Params | Resultado | Descripción |
|--------|--------|-----------|-------------|
| `sync.ejecutar` | `{ plan_id: string, modo_prueba: bool }` | `ResultadoEjecucion` | Ejecuta sincronización (o modo prueba). Se ejecuta en hilo separado |
| `sync.cancelar` | — | `{ ok: true }` | Cancela la sincronización en curso |
| `sync.reintentar_errores` | `{ plan_id: string, rutas: string[] }` | `ResultadoEjecucion` | Reintenta operaciones fallidas específicas |

### historial.*

| Método | Params | Resultado | Descripción |
|--------|--------|-----------|-------------|
| `historial.listar` | `{ pagina: int, limite: int }` | `{ items: ResumenHistorial[], total: int }` | Lista ejecuciones pasadas paginadas |
| `historial.obtener` | `{ id: string }` | `ResultadoEjecucion` | Detalle completo de una ejecución |
| `historial.eliminar` | `{ id: string }` | `{ ok: true }` | Elimina un registro del historial |

### sistema.*

| Método | Params | Resultado | Descripción |
|--------|--------|-----------|-------------|
| `sistema.seleccionar_directorio` | `{ titulo: string, ruta_inicial?: string }` | `{ ruta: string \| null }` | Abre el diálogo nativo de selección de carpeta |

---

## Eventos push (backend → frontend)

Los eventos no son llamadas JSON-RPC. El backend los envía mediante
`window.evaluate_js()` de pywebview, invocando un callback global en el
frontend.

### Mecanismo

```python
# Backend (Python)
import json

def emitir_evento(window, evento: EventoLog):
    evento_json = json.dumps(evento.to_dict())
    window.evaluate_js(f"window.__sincroniza_evento('{evento_json}')")
```

```typescript
// Frontend (TypeScript)
window.__sincroniza_evento = (eventoJson: string) => {
  const evento = JSON.parse(eventoJson);
  // Procesar según evento.tipo
};
```

### Estructura de un evento

```json
{
  "tipo": "progreso_analisis",
  "nivel": "info",
  "mensaje": "Procesados 1.234 de ~5.000 elementos",
  "datos": {
    "procesados": 1234,
    "estimado_total": 5000,
    "fase": "exploracion_origen"
  },
  "timestamp": "2026-03-27T10:32:01.456Z"
}
```

### Tipos de evento

| Tipo | Nivel habitual | Descripción |
|------|---------------|-------------|
| `analisis_iniciado` | info | Comienza el análisis |
| `progreso_analisis` | info | Progreso periódico durante el análisis |
| `analisis_completado` | info | Análisis terminado con éxito |
| `analisis_error` | error | Error durante el análisis |
| `sync_iniciada` | info | Comienza la sincronización |
| `progreso_sync` | info | Operación individual completada |
| `sync_completada` | info | Sincronización terminada |
| `sync_cancelada` | warning | Sincronización cancelada por el usuario |
| `sync_error` | error | Error durante la sincronización |
| `operacion_completada` | info | Una copia/reemplazo/eliminación concluyó |
| `operacion_fallida` | error | Una operación individual falló |
| `validacion_resultado` | info/warning | Resultado de validaciones |
| `conflicto_detectado` | warning | Archivo con patrón de conflicto de nube |
| `advertencia_eliminaciones` | warning | Se superó el umbral de eliminaciones |
| `log_general` | info/warning/error | Mensaje genérico de log |

---

## Ejemplo de flujo completo: análisis → sincronización

```
Frontend                                Backend
   │                                       │
   │  analisis.ejecutar({perfil_id})       │
   │ ────────────────────────────────────► │
   │                                       │  [hilo worker]
   │                                       │  Explorar origen...
   │  ◄─── evento: analisis_iniciado       │
   │  ◄─── evento: progreso_analisis       │  (cada N elementos)
   │  ◄─── evento: progreso_analisis       │
   │                                       │  Explorar destino...
   │  ◄─── evento: progreso_analisis       │
   │                                       │  Comparar...
   │  ◄─── evento: analisis_completado     │
   │  ◄────────────────────────────────── │
   │  return PlanSincronizacion            │
   │                                       │
   │  [usuario confirma]                   │
   │                                       │
   │  sync.ejecutar({plan_id, false})      │
   │ ────────────────────────────────────► │
   │                                       │  [hilo worker]
   │  ◄─── evento: sync_iniciada           │
   │  ◄─── evento: operacion_completada    │  (por cada operación)
   │  ◄─── evento: progreso_sync           │
   │  ◄─── evento: operacion_completada    │
   │  ◄─── evento: progreso_sync           │
   │  ◄─── evento: sync_completada         │
   │  ◄────────────────────────────────── │
   │  return ResultadoEjecucion            │
```
