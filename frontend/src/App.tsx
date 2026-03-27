/**
 * App — punto de entrada del árbol React.
 * Inicializa los stores, el sistema de eventos y determina qué página mostrar.
 */
import { useEffect, useState } from 'react'
import { useAppStore } from '@/state/useAppStore'
import { useLogStore } from '@/state/useLogStore'
import { useTemaStore } from '@/state/useTemaStore'
import { inicializarEventos } from '@/lib/eventos'
import { Layout } from '@/components/Layout'
import { PaginaPrincipal } from '@/pages/PaginaPrincipal'
import { PaginaOnboarding } from '@/pages/PaginaOnboarding'
import { PanelPerfiles } from '@/features/perfiles/PanelPerfiles'
import { PanelReglas } from '@/features/reglas/PanelReglas'
import { PanelHistorial } from '@/features/historial/PanelHistorial'

export default function App() {
  const { cargarPerfiles, cargarReglas, perfiles, vistaActual, setVista, procesarEvento } = useAppStore()
  const { agregar: logAgregar } = useLogStore()
  const { tema } = useTemaStore()
  const [inicializado, setInicializado] = useState(false)
  const [mostrarOnboarding, setMostrarOnboarding] = useState(false)

  // Aplicar clase de tema al documentElement
  useEffect(() => {
    const html = document.documentElement
    if (tema === 'oscuro') html.classList.add('dark')
    else html.classList.remove('dark')
  }, [tema])

  // Inicializar datos y eventos al montar
  useEffect(() => {
    const arrancar = async () => {
      inicializarEventos(logAgregar, procesarEvento)
      try {
        await Promise.all([cargarPerfiles(), cargarReglas()])
      } catch {
        // Sin bridge pywebview (desarrollo puro en navegador) — la UI arranca vacía
      }
      setInicializado(true)
    }
    arrancar()
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  // Detectar si hay que mostrar onboarding
  useEffect(() => {
    if (inicializado) {
      setMostrarOnboarding(perfiles.length === 0)
    }
  }, [inicializado, perfiles.length])

  // Atajos de teclado globales
  useEffect(() => {
    const { iniciarAnalisis, cancelarAnalisis, cancelarSync, perfilActivo, estadoAnalisis, estadoSync, expandirTodos, colapsarTodos, setBusquedaArbol } = useAppStore.getState()

    const handler = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return
      if (e.ctrlKey && e.key === 'a') {
        e.preventDefault()
        if (perfilActivo && estadoAnalisis !== 'analizando') iniciarAnalisis(perfilActivo.id)
      }
      if (e.ctrlKey && e.key === 'e') {
        e.preventDefault()
        expandirTodos()
      }
      if (e.ctrlKey && e.shiftKey && e.key === 'E') {
        e.preventDefault()
        colapsarTodos()
      }
      if (e.ctrlKey && e.key === 'f') {
        e.preventDefault()
        const input = document.querySelector<HTMLInputElement>('input[placeholder*="Buscar"]')
        if (input) { input.focus(); input.select() }
        else setBusquedaArbol('')
      }
      if (e.key === 'Escape') {
        if (estadoAnalisis === 'analizando') cancelarAnalisis()
        if (estadoSync === 'ejecutando') cancelarSync()
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [])

  if (!inicializado) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="animate-spin w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full" />
      </div>
    )
  }

  if (mostrarOnboarding && vistaActual !== 'historial' && vistaActual !== 'reglas' && vistaActual !== 'perfiles') {
    return (
      <Layout
        onNuevoPerfil={() => setVista('perfiles')}
        onGestionarReglas={() => setVista('reglas')}
        onVerHistorial={() => setVista('historial')}
      >
        <PaginaOnboarding onPerfilCreado={() => setMostrarOnboarding(false)} />
      </Layout>
    )
  }

  const renderContenido = () => {
    switch (vistaActual) {
      case 'historial':
        return <PanelHistorial />
      case 'reglas':
        return <PanelReglas />
      case 'perfiles':
        return <PanelPerfiles />
      default:
        return <PaginaPrincipal />
    }
  }

  return (
    <Layout
      onNuevoPerfil={() => setVista('perfiles')}
      onGestionarReglas={() => setVista('reglas')}
      onVerHistorial={() => setVista('historial')}
    >
      {renderContenido()}
    </Layout>
  )
}
