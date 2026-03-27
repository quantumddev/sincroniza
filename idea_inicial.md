Eres un agente de VSCode experto en crear aplicaciones de escritorio modernas y funcionales. Tu tarea es generar un proyecto de aplicación de escritorio **personal para sincronización espejo de directorios**, según estas especificaciones detalladas. No inventes detalles que no se mencionan aquí y no modifiques archivos fuera del proyecto.

---

# 1) Objetivo del proyecto
Crear una app de escritorio que permita copiar y sincronizar **un directorio origen a un directorio destino**, de forma que el destino quede **fiel al origen** tras aplicar reglas de exclusión configurables.  
- La sincronización debe ser **espejo inteligente unidireccional**:  
  - Copiar nuevos archivos/carpetas  
  - Reemplazar archivos modificados  
  - Eliminar archivos/carpetas que existen en destino pero ya no en origen  
  - Eliminar archivos/carpetas excluidos si existen en destino  
  - Conservar archivos idénticos  
- Todo esto debe **informar al usuario antes de ejecutar**, mostrando un árbol de diferencias completo y visualmente codificado.

---

# 2) Stack tecnológico
- **Backend:** Python 3.x, usando `pywebview` para exponer funciones al frontend.  
- **Frontend:** Vite + React + TailwindCSS.  
- **UI:** moderna, intuitiva y elegante, con soporte claro/oscuro con conmutador.  
- **Persistencia:** archivos JSON locales en `data/settings.json` (configuración) y `data/nombre_archivo.json` (historial de ejecuciones).  

---

# 3) Backend - responsabilidades
- Exploración de archivos y carpetas del origen y destino.
- Aplicación de reglas de exclusión (glob patterns).  
- Comparación de archivos:
  - Tamaño + fecha
  - Hash opcional según elección del usuario
- Sincronización espejo inteligente:
  - Copiar nuevos  
  - Reemplazar modificados  
  - Eliminar sobrantes  
  - Eliminar elementos excluidos si existen en destino  
- Gestión de errores:
  - Bloqueantes detienen la ejecución y muestran mensaje al usuario
  - Otros errores se guardan en JSON, se muestran y pueden reintentarse individualmente  
- Persistencia de configuración (`data/settings.json`) y historial (`data/*.json`).  
- Validaciones de seguridad:
  - Evita origen/destino iguales
  - Evita rutas anidadas peligrosas
  - Origen: `C:/Users/jaime/` (no OneDrive)
  - Destino: `C:/Users/jaime/OneDrive/...`
- No se realizan verificaciones de OneDrive en ejecución.  

---

# 4) Frontend - responsabilidades
- UI moderna y elegante, con:
  - Selección de rutas origen y destino mediante exploradores de archivos
  - Configuración de reglas de exclusión:
    - Activar/desactivar reglas
    - Crear, editar y eliminar reglas
    - Diferenciación por tipo: carpeta, archivo o ambos
  - Selección del método de comparación: tamaño+fecha o hash
  - Árbol de diferencias completo y visual:
    - 🟢 Nuevos
    - 🟡 Modificados
    - 🔴 Eliminados
    - ⚪ Sin cambios
    - 🚫 Excluidos
    - Archivos con errores marcados para localizar y reintentar
  - Panel de resumen con totales de cada categoría
  - Panel de log/consola con mensajes de análisis y ejecución
  - Botones de acción: Analizar, Modo Prueba (solo visual), Sincronizar, Cancelar
- El árbol es **informativo**; solo permite interacción para errores/conflictos
- Tema conmutador claro/oscuro, diseño elegante y moderno
- Idioma: español  

---

# 5) Flujo de usuario
1. Selección de **origen** y **destino**  
2. Validaciones de seguridad automáticas  
3. Análisis de diferencias y reglas aplicadas  
4. Presentación de **árbol de diferencias** con colores y resumen  
5. Confirmación explícita del usuario antes de ejecutar sincronización  
6. Ejecución de sincronización espejo inteligente  
7. Guardado de historial en JSON local  
8. Manejo de errores y reintentos individuales  

---

# 6) Reglas de exclusión (lista por defecto)
El backend debe soportar **glob patterns**. Las reglas por defecto son:
node_modules/**
venv/**
.venv/**
pycache/**
.pytest_cache/**
.mypy_cache/**
dist/**
build/**
coverage/**
.next/**
.nuxt/**
.cache/**
target/**
out/**
.git/**
.idea/**
.vscode/**
*.log
*.tmp
.DS_Store
Thumbs.db


- El usuario puede crear, editar, eliminar y activar/desactivar reglas.
- Diferenciación por tipo: carpeta, archivo o ambos.
- Las reglas se aplican tanto a archivos/carpetas nuevos como a los que existen en destino (para eliminar si corresponde).  

---

# 7) Persistencia
- `data/settings.json`: guarda configuración general y directorios seleccionados  
- `data/*.json`: guarda historial completo de cada ejecución con:
  - Archivos copiados, modificados, eliminados, idénticos  
  - Árbol genérico  
  - Errores  
  - Método de comparación usado  
  - Fecha y hora  

---

# 8) Validaciones de seguridad y restricciones
- Evitar origen = destino
- Bloquear si origen dentro de destino o destino dentro de origen
- Origen: solo `C:/Users/jaime/` (no OneDrive)
- Destino: solo OneDrive `C:/Users/jaime/OneDrive/...`  
- Si hay archivos abiertos/bloqueados:
  - La sincronización bloqueante se detiene con mensaje
  - Otros errores se registran y se pueden reintentar individualmente
- No hay límite de tamaño de archivos ni barra de progreso  

---

# 9) Filosofía de diseño
- Backend = toda la lógica de filesystem, comparación, sincronización, persistencia, manejo de errores  
- Frontend = UI, estado, visualización de árbol, botones y paneles  
- Árbol de diferencias **solo informativo**, excepto para errores/conflictos donde se permite acción  
- Sincronización espejo inteligente, resultado final: destino idéntico al origen tras aplicar reglas  
- Modo prueba = solo análisis y visualización, nunca modifica archivos  

---

# 10) Arquitectura de carpetas propuesta
/backend
/app
/services # lógica de filesystem, comparación y sincronización
/core # funciones de apoyo, hashing, validaciones
main.py # entrypoint del backend
/venv # entorno virtual existente
/frontend
/src
/components # UI reusable
/pages # pantalla principal
/state # estado y hooks
App.jsx
main.jsx
index.html
tailwind.config.js
vite.config.js
/data
settings.json
historial_*.json
/package.json
/README.md


---

# 11) Reglas adicionales para el agente
- No modificar archivos fuera del proyecto  
- No sobrescribir el backend/venv existente  
- Comentar mínimamente cada función y módulo explicando su propósito  
- Generar todo en español y con nombres de variables y funciones claros  
- Estructura lista para desarrollo y futura compilación (PyInstaller, etc.)  

---

# 12) Resultado esperado
El agente debe generar un proyecto **funcional, moderno y seguro**, que cumpla con:
- Sincronización espejo unidireccional con previsualización  
- UI con árbol de diferencias codificado por colores  
- Configuración y reglas de exclusión completas y editables  
- Persistencia de configuración e historial en JSON  
- Manejo robusto de errores y reintentos individuales  
- Arquitectura backend/frontend clara y separada  

---

**Instrucciones finales para el agente:**  
Genera el proyecto completo respetando todas estas especificaciones. No omitas ningún detalle. Asegúrate de que el backend gestione toda la lógica de filesystem y el frontend sea solo UI/estado. Implementa el árbol de diferencias con colores, resumen visual y panel de log. Todo debe ser seguro, moderno y elegante.