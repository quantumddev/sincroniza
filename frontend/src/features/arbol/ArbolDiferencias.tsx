/**
 * ArbolDiferencias — árbol virtualizado del plan de sincronización.
 * Aplana el árbol recursivo, filtra por estado y búsqueda,
 * y renderiza con @tanstack/react-virtual para rendimiento.
 */
import { useRef, useMemo } from 'react'
import { useVirtualizer } from '@tanstack/react-virtual'
import type { NodoArbolDatos, NodoAplanado, EstadoNodo } from '@/lib/tipos'
import { useAppStore } from '@/state/useAppStore'
import { NodoArbol } from './NodoArbol'
import { BusquedaArbol } from './BusquedaArbol'
import { FiltrosArbol } from './FiltrosArbol'
import { EstadoVacio } from '@/components/EstadoVacio'
import { BotonAccion } from '@/components/BotonAccion'

// ── Aplanado del árbol ────────────────────────────────────────────────────────

function aplanarArbol(
  nodo: NodoArbolDatos,
  nodosExpandidos: Set<string>,
  filtros: EstadoNodo[],
  busqueda: string,
  nivel: number,
  resultado: NodoAplanado[],
) {
  // Filtrar por búsqueda (nombre coincide)
  const q = busqueda.toLowerCase()
  const nombreCoincide = !q || nodo.nombre.toLowerCase().includes(q)

  // Filtrar por estado (si hay filtros activos)
  const estadoCoincide = filtros.length === 0 || filtros.includes(nodo.estado)

  const esCarpeta = nodo.tipo === 'CARPETA'
  const tieneHijos = nodo.hijos.length > 0

  // Las carpetas se muestran si algún hijo coincide o si ella misma coincide
  if (esCarpeta) {
    // Mostrar el nodo carpeta y procesar hijos si está expandida
    const esRaiz = nivel === 0
    if (!esRaiz) {
      resultado.push({
        id: nodo.ruta_relativa,
        nombre: nodo.nombre,
        ruta_relativa: nodo.ruta_relativa,
        tipo: nodo.tipo,
        estado: nodo.estado,
        tamaño: nodo.tamaño,
        tamaño_destino: nodo.tamaño_destino,
        motivo: nodo.motivo,
        nivel,
        tieneHijos,
        expandido: nodosExpandidos.has(nodo.ruta_relativa),
      })
    }

    if (esRaiz || nodosExpandidos.has(nodo.ruta_relativa)) {
      for (const hijo of nodo.hijos) {
        aplanarArbol(hijo, nodosExpandidos, filtros, busqueda, nivel + (esRaiz ? 0 : 1), resultado)
      }
    }
  } else {
    // Archivo — incluir si cumple filtros y búsqueda
    if (nombreCoincide && estadoCoincide) {
      resultado.push({
        id: nodo.ruta_relativa,
        nombre: nodo.nombre,
        ruta_relativa: nodo.ruta_relativa,
        tipo: nodo.tipo,
        estado: nodo.estado,
        tamaño: nodo.tamaño,
        tamaño_destino: nodo.tamaño_destino,
        motivo: nodo.motivo,
        nivel,
        tieneHijos: false,
        expandido: false,
      })
    }
  }
}

// ── Componente ────────────────────────────────────────────────────────────────

export function ArbolDiferencias() {
  const {
    planActual,
    filtrosArbol,
    busquedaArbol,
    nodosExpandidos,
    expandirTodos,
    colapsarTodos,
  } = useAppStore()

  const scrollRef = useRef<HTMLDivElement>(null)

  const items = useMemo<NodoAplanado[]>(() => {
    if (!planActual) return []
    const result: NodoAplanado[] = []
    aplanarArbol(planActual.arbol, nodosExpandidos, filtrosArbol, busquedaArbol, 0, result)
    return result
  }, [planActual, nodosExpandidos, filtrosArbol, busquedaArbol])

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => scrollRef.current,
    estimateSize: () => 28,
    overscan: 5,
  })

  if (!planActual) {
    return (
      <EstadoVacio
        titulo="Sin análisis"
        descripcion="Ejecuta un análisis para ver las diferencias entre origen y destino."
      />
    )
  }

  return (
    <div className="flex flex-col h-full gap-2">
      {/* Controles */}
      <div className="flex flex-col gap-2 shrink-0">
        <div className="flex items-center gap-2">
          <BusquedaArbol />
          <div className="flex gap-1 shrink-0">
            <BotonAccion variante="fantasma" onClick={expandirTodos} title="Expandir todo">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
              </svg>
            </BotonAccion>
            <BotonAccion variante="fantasma" onClick={colapsarTodos} title="Colapsar todo">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 9V4.5M9 9H4.5M9 9L3.75 3.75M9 15v4.5M9 15H4.5M9 15l-5.25 5.25M15 9h4.5M15 9V4.5M15 9l5.25-5.25M15 15h4.5M15 15v4.5m0-4.5l5.25 5.25" />
              </svg>
            </BotonAccion>
          </div>
        </div>
        <FiltrosArbol />
      </div>

      {/* Lista virtualizada */}
      {items.length === 0 ? (
        <div className="flex-1 flex items-center justify-center text-sm text-gray-400 dark:text-gray-500">
          No hay elementos que coincidan con los filtros.
        </div>
      ) : (
        <div
          ref={scrollRef}
          className="flex-1 overflow-y-auto"
        >
          <div
            style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative' }}
          >
            {virtualizer.getVirtualItems().map(vi => (
              <div
                key={vi.key}
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: '100%',
                  transform: `translateY(${vi.start}px)`,
                  height: `${vi.size}px`,
                }}
              >
                <NodoArbol
                  nodo={items[vi.index]}
                  style={{ height: `${vi.size}px` }}
                />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
