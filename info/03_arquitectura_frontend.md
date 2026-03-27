# Arquitectura del frontend — Sincroniza

---

## Visión general

El frontend es una aplicación React servida dentro de una ventana pywebview. No
existe servidor web convencional; el HTML/JS se carga directamente desde disco.

La comunicación con el backend se realiza exclusivamente a través de:
- **Llamadas JSON-RPC 2.0** (frontend → backend) vía el bridge de pywebview.
- **Eventos push** (backend → frontend) vía `window.evaluate_js()`.

---

## Stack

| Tecnología | Versión mínima | Propósito |
|------------|---------------|-----------|
| React | 18+ | UI declarativa |
| Vite | 5+ | Bundler y dev server |
| TailwindCSS | 4+ | Estilos utilitarios |
| Zustand | 4+ | Estado global ligero |
| @tanstack/react-virtual | 3+ | Virtualización del árbol |
| TypeScript | 5+ | Tipado estático del frontend |

---

## Estructura de carpetas

```
frontend/
├── index.html
├── package.json
├── tailwind.config.js
├── vite.config.js
├── tsconfig.json
├── src/
│   ├── main.tsx                  # Punto de entrada React
│   ├── App.tsx                   # Shell principal + routing de layout
│   ├── lib/
│   │   ├── rpc.ts                # Cliente JSON-RPC 2.0
│   │   ├── eventos.ts            # Receptor de eventos push del backend
│   │   ├── tipos.ts              # Tipos TypeScript compartidos
│   │   └── formato.ts            # Helpers de formateo (tamaños, fechas, etc.)
│   ├── state/
│   │   ├── useAppStore.ts        # Store Zustand principal
│   │   ├── useLogStore.ts        # Store de eventos de log
│   │   └── useTeemaStore.ts      # Store de tema claro/oscuro
│   ├── components/
│   │   ├── Layout.tsx            # Shell: sidebar + main + panel inferior
│   │   ├── Sidebar.tsx           # Panel lateral de perfiles
│   │   ├── BotonAccion.tsx       # Botón reutilizable con estados
│   │   ├── DialogoConfirmacion.tsx # Modal de confirmación
│   │   ├── SelectorRuta.tsx      # Input + botón para elegir directorio
│   │   ├── ConmutadorTema.tsx    # Toggle claro/oscuro
│   │   └── EstadoVacio.tsx       # Placeholder para listas vacías
│   ├── features/
│   │   ├── perfiles/
│   │   │   ├── PanelPerfiles.tsx
│   │   │   ├── FormularioPerfil.tsx
│   │   │   └── TarjetaPerfil.tsx
│   │   ├── reglas/
│   │   │   ├── PanelReglas.tsx
│   │   │   ├── FormularioRegla.tsx
│   │   │   └── FilaRegla.tsx
│   │   ├── analisis/
│   │   │   ├── PanelConfiguracion.tsx   # Origen, destino, método, botones
│   │   │   ├── PanelResumen.tsx         # Resumen numérico y de tamaño
│   │   │   └── BarraProgreso.tsx        # Progreso por fases
│   │   ├── arbol/
│   │   │   ├── ArbolDiferencias.tsx     # Componente principal virtualizado
│   │   │   ├── NodoArbol.tsx            # Fila individual del árbol
│   │   │   ├── FiltrosArbol.tsx         # Chips de filtro por estado
│   │   │   ├── BusquedaArbol.tsx        # Input de búsqueda
│   │   │   └── IndicadorEstado.tsx      # Badge de color por estado
│   │   ├── log/
│   │   │   ├── PanelLog.tsx             # Panel inferior con auto-scroll
│   │   │   └── EntradaLog.tsx           # Fila individual de log
│   │   └── historial/
│   │       ├── PanelHistorial.tsx
│   │       ├── FilaHistorial.tsx
│   │       └── DetalleEjecucion.tsx
│   └── pages/
│       ├── PaginaPrincipal.tsx          # Vista principal de sincronización
│       └── PaginaOnboarding.tsx         # Primera ejecución
```

---

## Gestión de estado (Zustand)

### useAppStore — estado principal

```typescript
interface AppState {
  // Perfil
  perfilActivo: Perfil | null;
  perfiles: Perfil[];

  // Análisis
  planActual: PlanSincronizacion | null;
  estadoAnalisis: 'inactivo' | 'analizando' | 'completado' | 'error';

  // Sincronización
  estadoSync: 'inactivo' | 'ejecutando' | 'completado' | 'cancelado' | 'error';
  progresoSync: { completadas: number; total: number } | null;

  // Reglas
  reglasGlobales: Regla[];

  // Historial
  historial: ResumenHistorial[];

  // UI
  filtrosArbol: EstadoNodo[];
  busquedaArbol: string;
  pendingSyncDetectado: boolean;
}
```

### useLogStore — eventos de log

```typescript
interface LogState {
  eventos: EventoLog[];
  agregar: (evento: EventoLog) => void;
  limpiar: () => void;
}
```

### useTemaStore — tema visual

```typescript
interface TemaState {
  tema: 'claro' | 'oscuro';
  alternar: () => void;
}
```

---

## Comunicación con el backend

### Llamadas RPC (frontend → backend)

```typescript
// lib/rpc.ts
async function llamarRpc<T>(metodo: string, params?: Record<string, unknown>): Promise<T> {
  const id = crypto.randomUUID();
  const peticion = { jsonrpc: '2.0', id, method: metodo, params };
  const respuestaRaw = await window.pywebview.api.ejecutar_rpc(JSON.stringify(peticion));
  const respuesta = JSON.parse(respuestaRaw);
  if (respuesta.error) {
    throw new RpcError(respuesta.error.code, respuesta.error.message, respuesta.error.data);
  }
  return respuesta.result as T;
}
```

### Eventos push (backend → frontend)

```typescript
// lib/eventos.ts
// El backend invoca: window.evaluate_js("window.__sincroniza_evento(JSON)")
window.__sincroniza_evento = (eventoJson: string) => {
  const evento: EventoLog = JSON.parse(eventoJson);
  useLogStore.getState().agregar(evento);

  // Eventos especiales actualizan el store principal
  if (evento.tipo === 'progreso_sync') {
    useAppStore.getState().actualizarProgreso(evento.datos);
  }
};
```

---

## Sistema de layout

```
┌──────────────────────────────────────────────────────┐
│  Barra superior: nombre app, perfil activo, tema     │
├───────────┬──────────────────────────────────────────┤
│           │                                          │
│  Sidebar  │  Zona central                            │
│           │                                          │
│  Perfiles │  ┌─ Configuración ──────────────────┐    │
│           │  │ Origen | Destino | Método        │    │
│           │  │ [Analizar] [Prueba] [Sincronizar]│    │
│           │  └──────────────────────────────────┘    │
│           │                                          │
│           │  ┌─ Resumen ────────────────────────┐    │
│           │  │ Nuevos: 42  Modif: 12  Elim: 5   │    │
│           │  └──────────────────────────────────┘    │
│           │                                          │
│           │  ┌─ Árbol de diferencias ───────────┐    │
│           │  │ [Filtros] [Búsqueda]             │    │
│           │  │                                  │    │
│           │  │  📁 src/                        │    │
│           │  │    📄 index.ts        🟢 Nuevo  │    │
│           │  │    📄 app.ts          🟡 Modif  │    │
│           │  │  📁 old/              🔴 Elim   │    │
│           │  │                                  │    │
│           │  └──────────────────────────────────┘    │
│           │                                          │
├───────────┴──────────────────────────────────────────┤
│  Panel de log (colapsable)                           │
│  [INFO]  10:32:01  Análisis iniciado                 │
│  [INFO]  10:32:03  1.234 elementos procesados        │
│  [WARN]  10:32:03  Detectado conflicto: archivo (1)  │
└──────────────────────────────────────────────────────┘
```

---

## Virtualización del árbol

El componente `ArbolDiferencias.tsx` usa `@tanstack/react-virtual` para renderizar
solo los nodos visibles en el viewport.

Estrategia:
1. El árbol jerárquico del backend se aplana en una lista donde cada nodo
   tiene un nivel de profundidad.
2. Los nodos colapsados ocultan sus hijos de la lista aplanada.
3. Solo se renderizan las filas visibles + un margen de overscan.
4. Los filtros y la búsqueda modifican la lista aplanada sin tocar el árbol
   original.

---

## Código visual por estado

| Estado | Color fondo | Icono | Clase TailwindCSS |
|--------|------------|-------|-------------------|
| Nuevo | verde suave | 🟢 | `bg-green-50 dark:bg-green-950 text-green-700 dark:text-green-300` |
| Modificado | amarillo suave | 🟡 | `bg-yellow-50 dark:bg-yellow-950 text-yellow-700 dark:text-yellow-300` |
| Eliminado | rojo suave | 🔴 | `bg-red-50 dark:bg-red-950 text-red-700 dark:text-red-300` |
| Idéntico | gris neutro | ⚪ | `text-gray-400 dark:text-gray-500` |
| Excluido | gris tachado | 🚫 | `text-gray-400 line-through` |
| Error | rojo intenso | ❌ | `bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200` |
| Conflicto nube | naranja | ⚠️ | `bg-orange-50 dark:bg-orange-950 text-orange-700 dark:text-orange-300` |
| Omitido | gris claro | ➖ | `text-gray-300 dark:text-gray-600` |

---

## Atajos de teclado

Implementados como un hook global `useAtajosTeclado()` montado en `App.tsx`.

| Atajo | Acción | Condición |
|-------|--------|-----------|
| `Ctrl+A` | Ejecutar análisis | Perfil activo y no hay operación en curso |
| `Ctrl+S` | Abrir diálogo de sincronización | Plan actual disponible |
| `Ctrl+F` | Foco en búsqueda del árbol | Siempre |
| `Ctrl+E` | Expandir/colapsar todo | Árbol visible |
| `Escape` | Cancelar operación en curso | Operación activa |

---

## Flujo de onboarding

```
¿Existen perfiles?
  │
  ├─ NO ──► PaginaOnboarding
  │           │
  │           ├─ "Crear primer perfil"
  │           │     └─► FormularioPerfil
  │           │
  │           └─ "Seleccionar rutas rápido"
  │                 └─► PanelConfiguracion (sin perfil guardado)
  │
  └─ SÍ ──► PaginaPrincipal (carga último perfil usado)
```

---

## Diálogo de confirmación de sincronización

Antes de ejecutar `sync.ejecutar`, se muestra un modal que incluye:

1. Resumen del plan: nuevos, modificados, eliminados con tamaños.
2. **Si hay eliminaciones**, se destacan en rojo con texto: "Se eliminarán X
   archivos (Y MB) del destino".
3. Si las eliminaciones superan el umbral → advertencia adicional en naranja.
4. Checkbox: "Confirmo que quiero ejecutar esta sincronización".
5. Botón "Sincronizar" habilitado solo tras marcar el checkbox.

---

## Modo desarrollo vs producción

| Modo | Carga del frontend | Comando |
|------|-------------------|---------|
| Desarrollo | pywebview apunta a `http://localhost:5173` (Vite dev server) | `npm run dev` + `python main.py --dev` |
| Producción | pywebview carga `frontend/dist/index.html` del disco | `npm run build` + `python main.py` |
