import { useState } from 'react';
import { AlertCircle, CheckCircle } from 'lucide-react';
import { api } from '../lib/api';
import type { Alerta } from '../lib/types';

interface Props {
  alertas: Alerta[];
  onUpdate: () => void;
}

export default function AlertasPanel({ alertas, onUpdate }: Props) {
  const [processingId, setProcessingId] = useState<number | null>(null);

  async function handleResolve(alertaId: number) {
    setProcessingId(alertaId);
    try {
      await api.resolveAlerta(alertaId);
      await onUpdate();
    } catch (error) {
      console.error('Error resolving alert:', error);
      alert('No se pudo resolver la alerta.');
    } finally {
      setProcessingId(null);
    }
  }

  //Traducción de mensajes técnicos a lenguaje claro
  function formatMensaje(mensaje: string) {
    return mensaje
      .replace(/numeric coordinates/gi, 'Ubicación en zona crítica')
      .replace(/descripcion: no/gi, 'Información incompleta del incidente')
      .replace(/description: no/gi, 'Información incompleta del incidente');
  }

  function getCriticidadColor(nivel: string | null) {
    switch (nivel) {
      case 'Critico':
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
    const baseClass = 'h-5 w-5';
    switch (nivel) {
      case 'Critico':
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
    <div className="rounded-xl border border-gray-100 bg-white p-6 shadow-lg">
      <h2 className="mb-4 text-lg font-bold text-gray-900">Alertas operacionales</h2>

      <div className="max-h-96 space-y-3 overflow-y-auto">
        {alertas.map((alerta) => (
          <div
            key={alerta.id}
            className={`rounded-lg border p-4 transition hover:shadow-md ${getCriticidadColor(alerta.nivel_criticidad)}`}
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex flex-1 items-start gap-3">
                {getCriticidadIcon(alerta.nivel_criticidad)}

                <div className="flex-1">
                  <div className="mb-1 flex items-center gap-2">
                    <span className="font-semibold text-gray-900">
                      {alerta.tipo_alerta}
                    </span>
                    <span className="text-xs text-gray-500">
                      {new Date(alerta.fecha_generacion).toLocaleDateString('es-AR')}
                    </span>
                  </div>

              
                  <p className="text-xs font-semibold text-gray-500">
                    Factores de riesgo:
                  </p>

                  
                  <p className="mb-2 text-sm text-gray-700">
                    {formatMensaje(alerta.mensaje)}
                  </p>
                   <pre className="text-xs text-red-500">
                    {JSON.stringify(alerta, null, 2)}
                    </pre>
                  {alerta.aeropuertos && (
                    <p className="text-xs text-gray-600">
                      Aeropuerto: {alerta.aeropuertos.nombre}
                    </p>
                  )}

                  {alerta.score_predictivo !== null &&
                    alerta.score_predictivo !== undefined && (
                      <p className="text-xs text-gray-600">
                        Score predictivo: {alerta.score_predictivo}%
                      </p>
                    )}
                </div>
              </div>

              <button
                onClick={() => handleResolve(alerta.id)}
                disabled={processingId === alerta.id}
                className="flex items-center gap-1 rounded-lg bg-green-100 px-3 py-1 text-xs text-green-700 transition hover:bg-green-200 disabled:opacity-50"
              >
                <CheckCircle className="h-3 w-3" />
                {processingId === alerta.id ? 'Resolviendo...' : 'Resolver'}
              </button>
            </div>
          </div>
        ))}

        {alertas.length === 0 && (
          <div className="py-12 text-center">
            <CheckCircle className="mx-auto mb-3 h-12 w-12 text-green-500" />
            <p className="text-gray-500">No hay alertas pendientes</p>
            <p className="mt-1 text-sm text-gray-400">
              Todas las alertas están resueltas.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
