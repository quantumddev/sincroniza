# Estructura de carpetas — Sincroniza

Este documento describe la estructura completa del proyecto, el propósito de
cada directorio y archivo relevante.

---

## Árbol completo

```
30_Sincroniza/
├── README.md                           # Documentación principal del repositorio
├── idea_inicial.md                     # Especificación funcional del producto
│
├── info/                               # Documentación técnica del proyecto
│   ├── 01_plan_implementacion.md       # Plan de fases y tareas
│   ├── 02_arquitectura_backend.md      # Diseño del backend
│   ├── 03_arquitectura_frontend.md     # Diseño del frontend
│   ├── 04_protocolo_jsonrpc.md         # Contrato JSON-RPC 2.0
│   ├── 05_modelos_datos.md             # Definición de modelos de datos
│   └── 06_estructura_carpetas.md       # Este documento
│
├── backend/
│   ├── main.py                         # Entrypoint: pywebview + API
│   ├── requirements.txt                # Dependencias Python fijadas
│   ├── venv/                           # Entorno virtual (no versionado)
│   ├── app/
│   │   ├── __init__.py
│   │   │
│   │   ├── api/                        # Capa de comunicación JSON-RPC
│   │   │   ├── __init__.py
│   │   │   ├── dispatcher.py           # Parseo, despacho y respuesta JSON-RPC
│   │   │   ├── registro.py             # Mapeo de métodos a servicios
│   │   │   └── eventos.py              # Push de eventos al frontend via evaluate_js
│   │   │
│   │   ├── models/                     # Dataclasses con type hints
│   │   │   ├── __init__.py
│   │   │   ├── enums.py                # EstadoNodo, MetodoComparacion, TipoRegla, etc.
│   │   │   ├── regla.py                # Modelo Regla
│   │   │   ├── perfil.py               # Modelo Perfil
│   │   │   ├── nodo_arbol.py           # Modelo NodoArbol
│   │   │   ├── plan.py                 # PlanSincronizacion, OperacionPlanificada, ResumenPlan
│   │   │   ├── resultado.py            # ResultadoEjecucion
│   │   │   ├── error.py                # ErrorSincronizacion
│   │   │   ├── evento_log.py           # EventoLog
│   │   │   └── configuracion.py        # ConfiguracionApp, PendingSync
│   │   │
│   │   ├── services/                   # Clases de servicio (lógica de negocio)
│   │   │   ├── __init__.py
│   │   │   ├── explorador.py           # ExploradorServicio
│   │   │   ├── comparador.py           # ComparadorServicio
│   │   │   ├── sincronizador.py        # SincronizadorServicio
│   │   │   ├── reglas.py               # ReglasServicio
│   │   │   ├── perfiles.py             # PerfilServicio
│   │   │   ├── historial.py            # HistorialServicio
│   │   │   ├── validador.py            # ValidadorServicio
│   │   │   └── log.py                  # LogServicio
│   │   │
│   │   ├── core/                       # Utilidades puras
│   │   │   ├── __init__.py
│   │   │   ├── normalizacion.py        # Normalización de rutas Windows
│   │   │   ├── validaciones.py         # Funciones de validación puras
│   │   │   ├── hashing.py              # Hash SHA-256 por bloques
│   │   │   ├── fingerprint.py          # Fingerprint del plan
│   │   │   ├── glob_matcher.py         # Evaluación de globs
│   │   │   └── fechas.py               # Utilidades de fechas
│   │   │
│   │   └── storage/                    # Persistencia en disco
│   │       ├── __init__.py
│   │       ├── config_storage.py       # settings.json
│   │       ├── historial_storage.py    # data/history/*.json
│   │       └── pending_storage.py      # data/pending_sync.json
│   │
│   └── tests/                          # Tests del backend
│       ├── __init__.py
│       ├── conftest.py                 # Fixtures compartidos (tmpdir, etc.)
│       ├── test_models/                # Tests de serialización de modelos
│       │   └── ...
│       ├── test_core/                  # Tests de utilidades
│       │   └── ...
│       ├── test_storage/               # Tests de persistencia
│       │   └── ...
│       ├── test_services/              # Tests de servicios
│       │   └── ...
│       └── test_api/                   # Tests del dispatcher JSON-RPC
│           └── ...
│
├── frontend/
│   ├── index.html                      # HTML base
│   ├── package.json                    # Dependencias npm
│   ├── tsconfig.json                   # Configuración TypeScript
│   ├── vite.config.ts                  # Configuración Vite
│   ├── tailwind.config.js              # Configuración TailwindCSS
│   ├── dist/                           # Build de producción (no versionado)
│   ├── node_modules/                   # Dependencias (no versionado)
│   └── src/
│       ├── main.tsx                    # Punto de entrada React
│       ├── App.tsx                     # Shell principal
│       │
│       ├── lib/                        # Utilidades compartidas del frontend
│       │   ├── rpc.ts                  # Cliente JSON-RPC 2.0
│       │   ├── eventos.ts              # Receptor de eventos push
│       │   ├── tipos.ts                # Tipos TypeScript (mirror de modelos backend)
│       │   └── formato.ts              # Formateo de tamaños, fechas, etc.
│       │
│       ├── state/                      # Stores Zustand
│       │   ├── useAppStore.ts          # Estado principal de la app
│       │   ├── useLogStore.ts          # Cola de eventos de log
│       │   └── useTemaStore.ts         # Tema claro/oscuro
│       │
│       ├── components/                 # Componentes reutilizables
│       │   ├── Layout.tsx
│       │   ├── Sidebar.tsx
│       │   ├── BotonAccion.tsx
│       │   ├── DialogoConfirmacion.tsx
│       │   ├── SelectorRuta.tsx
│       │   ├── ConmutadorTema.tsx
│       │   └── EstadoVacio.tsx
│       │
│       ├── features/                   # Módulos funcionales
│       │   ├── perfiles/
│       │   │   ├── PanelPerfiles.tsx
│       │   │   ├── FormularioPerfil.tsx
│       │   │   └── TarjetaPerfil.tsx
│       │   ├── reglas/
│       │   │   ├── PanelReglas.tsx
│       │   │   ├── FormularioRegla.tsx
│       │   │   └── FilaRegla.tsx
│       │   ├── analisis/
│       │   │   ├── PanelConfiguracion.tsx
│       │   │   ├── PanelResumen.tsx
│       │   │   └── BarraProgreso.tsx
│       │   ├── arbol/
│       │   │   ├── ArbolDiferencias.tsx
│       │   │   ├── NodoArbol.tsx
│       │   │   ├── FiltrosArbol.tsx
│       │   │   ├── BusquedaArbol.tsx
│       │   │   └── IndicadorEstado.tsx
│       │   ├── log/
│       │   │   ├── PanelLog.tsx
│       │   │   └── EntradaLog.tsx
│       │   └── historial/
│       │       ├── PanelHistorial.tsx
│       │       ├── FilaHistorial.tsx
│       │       └── DetalleEjecucion.tsx
│       │
│       └── pages/                      # Páginas de alto nivel
│           ├── PaginaPrincipal.tsx
│           └── PaginaOnboarding.tsx
│
└── data/                               # Datos de usuario (no versionado)
    ├── .gitkeep
    ├── settings.json                   # Configuración de la app
    ├── pending_sync.json               # Temporal durante ejecución (si existe)
    └── history/                        # Historial de ejecuciones
        ├── .gitkeep
        └── run_<uuid>.json             # Un archivo por ejecución
```

---

## Convenciones de nombrado

| Ámbito | Convención | Ejemplo |
|--------|-----------|---------|
| Módulos Python | snake_case | `config_storage.py` |
| Clases Python | PascalCase | `ExploradorServicio` |
| Funciones Python | snake_case | `normalizar_ruta()` |
| Variables Python | snake_case | `ruta_origen` |
| Enums Python | MAYUSCULAS | `EstadoNodo.NUEVO` |
| Componentes React | PascalCase | `ArbolDiferencias.tsx` |
| Hooks React | camelCase con prefijo `use` | `useAppStore.ts` |
| Utilidades TS | camelCase | `llamarRpc()` |
| Archivos JSON | snake_case | `settings.json`, `run_*.json` |

---

## Archivos no versionados (.gitignore)

```gitignore
# Python
backend/venv/
__pycache__/
*.pyc
.pytest_cache/

# Node
frontend/node_modules/
frontend/dist/

# Datos de usuario
data/settings.json
data/pending_sync.json
data/history/*.json

# IDE
.vscode/
.idea/
```

---

## Archivos de soporte para carpetas vacías

Se incluyen archivos `.gitkeep` en:
- `data/`
- `data/history/`

Estos se versionan para que Git preserve la estructura de carpetas.
