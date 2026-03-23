import { useState } from 'react';
import { supabase } from '../lib/supabase';
import { useAuth } from '../contexts/AuthContext';
import { AlertCircle, CheckCircle } from 'lucide-react';
import type { Database } from '../lib/database.types';

type Alerta = Database['public']['Tables']['alertas']['Row'] & {
  aeropuertos?: { nombre: string } | null;
};

interface Props {
  alertas: Alerta[];
  onUpdate: () => void;
}

export default function AlertasPanel({ alertas, onUpdate }: Props) {
  const { user } = useAuth();
  const [processingId, setProcessingId] = useState<number | null>(null);

  async function handleResolve(alertaId: number) {
    setProcessingId(alertaId);
    try {
      const { error } = await supabase
        .from('alertas')
        .update({
          estado: 'Resuelta',
          atendido_por: user?.id,
          fecha_resolucion: new Date().toISOString()
        })
        .eq('id', alertaId);

      if (error) throw error;
      await onUpdate();
    } catch (error) {
      console.error('Error resolving alert:', error);
      alert('Error al resolver la alerta');
    } finally {
      setProcessingId(null);
    }
  }

  function getCriticidadColor(nivel: string | null) {
    switch (nivel) {
      case 'Crítico':
      case 'Alta':
        return 'bg-red-50 border-red-300';
      case 'Media':
        return 'bg-orange-50 border-orange-300';
      case 'Baja':
        return 'bg-yellow-50 border-yellow-300';
      default:
        return 'bg-gray-50 border-gray-300';
    }
  }

  function getCriticidadIcon(nivel: string | null) {
    const baseClass = 'w-5 h-5';
    switch (nivel) {
      case 'Crítico':
      case 'Alta':
        return <AlertCircle className={`${baseClass} text-red-600`} />;
      case 'Media':
        return <AlertCircle className={`${baseClass} text-orange-600`} />;
      case 'Baja':
        return <AlertCircle className={`${baseClass} text-yellow-600`} />;
      default:
        return <AlertCircle className={`${baseClass} text-gray-600`} />;
    }
  }

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6">
      <h2 className="text-lg font-bold text-gray-900 mb-4">Alertas Operacionales</h2>
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {alertas.map((alerta) => (
          <div
            key={alerta.id}
            className={`border rounded-lg p-4 ${getCriticidadColor(alerta.nivel_criticidad)} transition hover:shadow-md`}
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-start gap-3 flex-1">
                {getCriticidadIcon(alerta.nivel_criticidad)}
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-semibold text-gray-900">{alerta.tipo_alerta}</span>
                    <span className="text-xs text-gray-500">
                      {new Date(alerta.fecha_generacion).toLocaleDateString('es-ES')}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700 mb-2">{alerta.mensaje}</p>
                  {alerta.aeropuertos && (
                    <p className="text-xs text-gray-600">
                      Aeropuerto: {alerta.aeropuertos.nombre}
                    </p>
                  )}
                  {alerta.score_predictivo && (
                    <p className="text-xs text-gray-600">
                      Score predictivo: {alerta.score_predictivo}%
                    </p>
                  )}
                </div>
              </div>
              <button
                onClick={() => handleResolve(alerta.id)}
                disabled={processingId === alerta.id}
                className="flex items-center gap-1 px-3 py-1 bg-green-100 text-green-700 text-xs rounded-lg hover:bg-green-200 transition disabled:opacity-50"
              >
                <CheckCircle className="w-3 h-3" />
                {processingId === alerta.id ? 'Resolviendo...' : 'Resolver'}
              </button>
            </div>
          </div>
        ))}
        {alertas.length === 0 && (
          <div className="text-center py-12">
            <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-3" />
            <p className="text-gray-500">No hay alertas pendientes</p>
            <p className="text-sm text-gray-400 mt-1">Todas las alertas están resueltas</p>
          </div>
        )}
      </div>
    </div>
  );
}
