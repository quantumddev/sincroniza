/**
 * FormularioPerfil — crear o editar un perfil de sincronización.
 */
import { useState } from 'react'
import type { Perfil, MetodoComparacion } from '@/lib/tipos'
import { llamarRpc } from '@/lib/rpc'
import { BotonAccion } from '@/components/BotonAccion'
import { SelectorRuta } from '@/components/SelectorRuta'
import { ETIQUETAS_METODO } from '@/lib/formato'
import { useAppStore } from '@/state/useAppStore'

interface FormularioPerfilProps {
  perfilEditar?: Perfil
  onCerrar: () => void
}

const METODOS: MetodoComparacion[] = ['TAMAÑO_FECHA', 'HASH']

export function FormularioPerfil({ perfilEditar, onCerrar }: FormularioPerfilProps) {
  const { cargarPerfiles, setPerfilActivo } = useAppStore()

  const [nombre, setNombre] = useState(perfilEditar?.nombre ?? '')
  const [origen, setOrigen] = useState(perfilEditar?.origen ?? '')
  const [destino, setDestino] = useState(perfilEditar?.destino ?? '')
  const [metodo, setMetodo] = useState<MetodoComparacion>(
    perfilEditar?.metodo_comparacion ?? 'TAMAÑO_FECHA',
  )
  const [umbral, setUmbral] = useState(String(perfilEditar?.umbral_eliminaciones ?? 10))
  const [guardando, setGuardando] = useState(false)
  const [error, setError] = useState('')

  const esEdicion = !!perfilEditar

  const guardar = async () => {
    if (!nombre.trim()) { setError('El nombre es obligatorio'); return }
    if (!origen.trim()) { setError('La ruta de origen es obligatoria'); return }
    if (!destino.trim()) { setError('La ruta de destino es obligatoria'); return }

    setGuardando(true)
    setError('')

    try {
      if (esEdicion) {
        const actualizado = await llamarRpc<Perfil>('perfil.actualizar', {
          id: perfilEditar.id,
          cambios: {
            nombre: nombre.trim(),
            origen: origen.trim(),
            destino: destino.trim(),
            metodo_comparacion: metodo,
            umbral_eliminaciones: parseInt(umbral) || 10,
          },
        })
        await cargarPerfiles()
        setPerfilActivo(actualizado)
      } else {
        const creado = await llamarRpc<Perfil>('perfil.crear', {
          perfil: {
            nombre: nombre.trim(),
            origen: origen.trim(),
            destino: destino.trim(),
            metodo_comparacion: metodo,
            umbral_eliminaciones: parseInt(umbral) || 10,
            // reglas_exclusion_ids se pobla automáticamente en el backend
            // con todas las reglas globales activas al crear el perfil
          },
        })
        await cargarPerfiles()
        setPerfilActivo(creado)
      }
      onCerrar()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error al guardar el perfil')
    } finally {
      setGuardando(false)
    }
  }

  return (
    <div className="flex flex-col gap-4 p-5">
      <h2 className="text-base font-semibold text-gray-900 dark:text-gray-100">
        {esEdicion ? 'Editar perfil' : 'Nuevo perfil'}
      </h2>

      {/* Nombre */}
      <div className="flex flex-col gap-1">
        <label className="text-xs font-medium text-gray-600 dark:text-gray-400">Nombre</label>
        <input
          type="text"
          value={nombre}
          onChange={e => setNombre(e.target.value)}
          placeholder="Ej: Fotos familiares"
          className="input-base"
          autoFocus
        />
      </div>

      {/* Origen */}
      <SelectorRuta
        id="origen"
        label="Directorio origen"
        valor={origen}
        onChange={setOrigen}
        titulo="Seleccionar origen"
        placeholder="Ruta al directorio origen…"
      />

      {/* Destino */}
      <SelectorRuta
        id="destino"
        label="Directorio destino"
        valor={destino}
        onChange={setDestino}
        titulo="Seleccionar destino"
        placeholder="Ruta al directorio destino…"
      />

      {/* Método de comparación */}
      <div className="flex flex-col gap-1">
        <label className="text-xs font-medium text-gray-600 dark:text-gray-400">
          Método de comparación
        </label>
        <select
          value={metodo}
          onChange={e => setMetodo(e.target.value as MetodoComparacion)}
          className="input-base"
        >
          {METODOS.map(m => (
            <option key={m} value={m}>{ETIQUETAS_METODO[m]}</option>
          ))}
        </select>
      </div>

      {/* Umbral eliminaciones */}
      <div className="flex flex-col gap-1">
        <label className="text-xs font-medium text-gray-600 dark:text-gray-400">
          Umbral de eliminaciones
          <span className="text-gray-400 ml-1 font-normal">(advertencia si se supera)</span>
        </label>
        <input
          type="number"
          min={0}
          max={9999}
          value={umbral}
          onChange={e => setUmbral(e.target.value)}
          className="input-base w-24"
        />
      </div>

      {error && (
        <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
      )}

      <div className="flex justify-end gap-2 pt-2 border-t border-gray-200 dark:border-gray-700">
        <BotonAccion variante="secundario" onClick={onCerrar} disabled={guardando}>
          Cancelar
        </BotonAccion>
        <BotonAccion onClick={guardar} cargando={guardando}>
          {esEdicion ? 'Guardar cambios' : 'Crear perfil'}
        </BotonAccion>
      </div>
    </div>
  )
}
