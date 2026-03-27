# Sincroniza

Aplicación de escritorio para Windows que sincroniza un directorio origen hacia
un directorio destino en modo **espejo inteligente unidireccional**.

El destino queda alineado con el origen tras aplicar reglas de exclusión
configurables. Antes de ejecutar cualquier cambio, la app muestra una
previsualización completa con un árbol de diferencias codificado por colores.

---

## Características principales

- Sincronización espejo unidireccional (origen → destino)
- Previsualización obligatoria antes de ejecutar
- Árbol de diferencias con filtros, búsqueda y virtualización
- Reglas de exclusión editables (glob patterns)
- Perfiles de sincronización reutilizables
- Modo prueba (solo análisis, sin escritura)
- Historial persistente de ejecuciones
- Gestión de errores con reintentos individuales
- Detección de conflictos de servicios de nube
- Resiliencia ante interrupciones (crash recovery)
- Interfaz moderna en español con tema claro/oscuro

---

## Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Backend | Python 3.x |
| Escritorio | pywebview |
| Frontend | React + TypeScript + Vite |
| Estilos | TailwindCSS |
| Estado | Zustand |
| Virtualización | @tanstack/react-virtual |
| Persistencia | JSON local |
| Comunicación | JSON-RPC 2.0 (in-process via pywebview) |

---

## Estructura del proyecto

```
30_Sincroniza/
├── backend/          # API Python + lógica de negocio
│   ├── app/
│   │   ├── api/      # Dispatcher JSON-RPC 2.0
│   │   ├── models/   # Dataclasses tipadas
│   │   ├── services/ # Clases de servicio
│   │   ├── core/     # Utilidades y validaciones
│   │   └── storage/  # Persistencia JSON
│   ├── tests/        # Tests unitarios e integración
│   └── main.py       # Entrypoint
├── frontend/         # UI React + TypeScript
│   └── src/
│       ├── components/
│       ├── features/
│       ├── pages/
│       ├── state/
│       └── lib/
├── data/             # Configuración e historial (no versionado)
├── info/             # Documentación técnica
└── idea_inicial.md   # Especificación funcional
```

---

## Documentación técnica

Toda la documentación del proyecto se encuentra en la carpeta `info/`:

| Documento | Contenido |
|-----------|----------|
| [01_plan_implementacion.md](info/01_plan_implementacion.md) | Plan completo de fases y tareas para construir el proyecto |
| [02_arquitectura_backend.md](info/02_arquitectura_backend.md) | Diseño del backend: paquetes, servicios, hilos, escritura segura |
| [03_arquitectura_frontend.md](info/03_arquitectura_frontend.md) | Diseño del frontend: componentes, stores, layout, virtualización |
| [04_protocolo_jsonrpc.md](info/04_protocolo_jsonrpc.md) | Contrato JSON-RPC 2.0: métodos, errores, eventos push |
| [05_modelos_datos.md](info/05_modelos_datos.md) | Definición completa de modelos, enums y relaciones |
| [06_estructura_carpetas.md](info/06_estructura_carpetas.md) | Árbol completo del proyecto con convenciones |

La especificación funcional del producto está en [idea_inicial.md](idea_inicial.md).

---

## Desarrollo

### Backend

```bash
cd backend
python -m venv venv          # Solo la primera vez
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python main.py --dev         # Modo desarrollo (apunta a Vite dev server)
```

### Frontend

```bash
cd frontend
npm install                  # Solo la primera vez
npm run dev                  # Vite dev server en localhost:5173
```

### Tests

```bash
cd backend
venv\Scripts\activate
pytest                       # Ejecutar todos los tests
pytest tests/test_core/      # Solo tests de core
```

---

## Build de producción

```bash
# 1. Compilar frontend
cd frontend
npm run build

# 2. Ejecutar app (carga dist/ desde disco)
cd ../backend
python main.py
```

Para generar un ejecutable standalone:

```bash
cd backend
pyinstaller --onefile --windowed main.py
```

---

## Licencia

Proyecto personal. Uso privado.
