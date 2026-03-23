import { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';
import { useAuth } from '../contexts/AuthContext';
import { X } from 'lucide-react';
import type { Database } from '../lib/database.types';

type Incidente = Database['public']['Tables']['incidentes']['Row'];
type Aeropuerto = Database['public']['Tables']['aeropuertos']['Row'];
type TipoIncidente = Database['public']['Tables']['tipos_incidente']['Row'];
type Aeronave = Database['public']['Tables']['aeronaves']['Row'];

interface Props {
  incidente: Incidente | null;
  onClose: () => void;
}

export default function IncidenteModal({ incidente, onClose }: Props) {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [aeropuertos, setAeropuertos] = useState<Aeropuerto[]>([]);
  const [tiposIncidente, setTiposIncidente] = useState<TipoIncidente[]>([]);
  const [aeronaves, setAeronaves] = useState<Aeronave[]>([]);

  const [formData, setFormData] = useState({
    aeropuerto_id: incidente?.aeropuerto_id || '',
    tipo_incidente_id: incidente?.tipo_incidente_id || '',
    aeronave_id: incidente?.aeronave_id || '',
    fecha_hora: incidente?.fecha_hora ? new Date(incidente.fecha_hora).toISOString().slice(0, 16) : '',
    descripcion: incidente?.descripcion || '',
    nivel_riesgo: incidente?.nivel_riesgo || 'Bajo',
    fase_vuelo: incidente?.fase_vuelo || '',
    latitud: incidente?.latitud || '',
    longitud: incidente?.longitud || ''
  });

  useEffect(() => {
    loadFormData();
  }, []);

  async function loadFormData() {
    try {
      const [aeropuertosRes, tiposRes, aeronavesRes] = await Promise.all([
        supabase.from('aeropuertos').select('*').order('nombre'),
        supabase.from('tipos_incidente').select('*').order('nombre'),
        supabase.from('aeronaves').select('*').order('matricula')
      ]);

      if (aeropuertosRes.data) setAeropuertos(aeropuertosRes.data);
      if (tiposRes.data) setTiposIncidente(tiposRes.data);
      if (aeronavesRes.data) setAeronaves(aeronavesRes.data);
    } catch (error) {
      console.error('Error loading form data:', error);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);

    try {
      const dataToSave = {
        aeropuerto_id: formData.aeropuerto_id ? parseInt(formData.aeropuerto_id as string) : null,
        tipo_incidente_id: formData.tipo_incidente_id ? parseInt(formData.tipo_incidente_id as string) : null,
        aeronave_id: formData.aeronave_id ? parseInt(formData.aeronave_id as string) : null,
        fecha_hora: formData.fecha_hora,
        descripcion: formData.descripcion,
        nivel_riesgo: formData.nivel_riesgo as 'Bajo' | 'Medio' | 'Alto' | 'Crítico',
        fase_vuelo: formData.fase_vuelo,
        latitud: formData.latitud ? parseFloat(formData.latitud as string) : null,
        longitud: formData.longitud ? parseFloat(formData.longitud as string) : null,
        reportado_por: user?.id || null
      };

      if (incidente) {
        const { error } = await supabase
          .from('incidentes')
          .update(dataToSave)
          .eq('id', incidente.id);
        if (error) throw error;
      } else {
        const { error } = await supabase
          .from('incidentes')
          .insert(dataToSave);
        if (error) throw error;
      }

      onClose();
    } catch (error) {
      console.error('Error saving incident:', error);
      alert('Error al guardar el incidente');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-200 p-6 flex items-center justify-between">
          <h2 className="text-xl font-bold text-gray-900">
            {incidente ? 'Editar Incidente' : 'Nuevo Incidente'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Aeropuerto
              </label>
              <select
                value={formData.aeropuerto_id}
                onChange={(e) => setFormData({ ...formData, aeropuerto_id: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Seleccionar aeropuerto</option>
                {aeropuertos.map((aeropuerto) => (
                  <option key={aeropuerto.id} value={aeropuerto.id}>
                    {aeropuerto.codigo_icao} - {aeropuerto.nombre}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tipo de Incidente
              </label>
              <select
                value={formData.tipo_incidente_id}
                onChange={(e) => setFormData({ ...formData, tipo_incidente_id: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Seleccionar tipo</option>
                {tiposIncidente.map((tipo) => (
                  <option key={tipo.id} value={tipo.id}>
                    {tipo.nombre}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Aeronave
              </label>
              <select
                value={formData.aeronave_id}
                onChange={(e) => setFormData({ ...formData, aeronave_id: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Seleccionar aeronave</option>
                {aeronaves.map((aeronave) => (
                  <option key={aeronave.id} value={aeronave.id}>
                    {aeronave.matricula} - {aeronave.modelo}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Fecha y Hora
              </label>
              <input
                type="datetime-local"
                value={formData.fecha_hora}
                onChange={(e) => setFormData({ ...formData, fecha_hora: e.target.value })}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nivel de Riesgo
              </label>
              <select
                value={formData.nivel_riesgo}
                onChange={(e) => setFormData({ ...formData, nivel_riesgo: e.target.value })}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="Bajo">Bajo</option>
                <option value="Medio">Medio</option>
                <option value="Alto">Alto</option>
                <option value="Crítico">Crítico</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Fase de Vuelo
              </label>
              <input
                type="text"
                value={formData.fase_vuelo}
                onChange={(e) => setFormData({ ...formData, fase_vuelo: e.target.value })}
                placeholder="ej: Despegue, Aterrizaje, Crucero"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Latitud
              </label>
              <input
                type="number"
                step="0.000001"
                value={formData.latitud}
                onChange={(e) => setFormData({ ...formData, latitud: e.target.value })}
                placeholder="-34.123456"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Longitud
              </label>
              <input
                type="number"
                step="0.000001"
                value={formData.longitud}
                onChange={(e) => setFormData({ ...formData, longitud: e.target.value })}
                placeholder="-58.123456"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Descripción
            </label>
            <textarea
              value={formData.descripcion}
              onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
              rows={4}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Describa el incidente en detalle..."
            />
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 bg-gradient-to-r from-sky-500 to-blue-600 text-white rounded-lg hover:from-sky-600 hover:to-blue-700 transition shadow-lg shadow-blue-500/30 disabled:opacity-50"
            >
              {loading ? 'Guardando...' : 'Guardar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
