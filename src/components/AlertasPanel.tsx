import { useState } from 'react';
import { AlertCircle, CheckCircle, MapPin, Moon, AlertTriangle } from 'lucide-react';
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

  /**
   * Limpia y traduce los mensajes técnicos del modelo de IA 
   * a un lenguaje comprensible para el operador.
   */
  function formatMensaje(mensaje: string) {
    if (!mensaje) return 'Sin detalles adicionales disponibles.';

    return mensaje
      // Traducir coordenadas
      .replace(/numeric\s*has\s*coordinates/gi, 'Ubicación en zona de riesgo crítico')
      .replace(/has\s*coordinates/gi, 'Ubicación georeferenciada')
      
      // Traducir horario nocturno
      .replace(/numeric\s*is\s*night/gi, 'Operación durante horario nocturno')
      .replace(/is\s*night/gi, 'Condición de baja visibilidad (Noche)')
      
      // Limpiar etiquetas de descripción vacía
      .replace(/descripcion\s*:\s*no/gi, 'Pendiente de descripción detallada')
      .replace(/description\s*:\s*no/gi, 'Pendiente de descripción detallada')
      
      // Limpiar prefijos técnicos genéricos
      .replace(/numeric\s+/gi, '')
      .trim();
  }

  function getCriticidadColor(nivel: string | null) {
    const n = nivel?.toLowerCase();
    if (n === 'critico' || n === 'crítico' || n === 'alta') return 'bg-red-50 border-red-200';
    if (n === 'media') return 'bg-orange-50 border-orange-200';
    if (n === 'baja') return 'bg-yellow-50 border-yellow-200';
    return 'bg-gray-50 border-gray-200';
  }

  function getCriticidadIcon(nivel: string | null) {
    const n = nivel?.toLowerCase();
    const baseClass = 'h-5 w-5';
    if (n === 'critico' || n === 'crítico' || n === 'alta') return <AlertCircle className={`${baseClass} text-red-600`} />;
    if (n === 'media') return <AlertTriangle className={`${baseClass} text-orange-600`} />;
    return <AlertCircle className={`${baseClass} text-yellow-600`} />;
  }

  return (
    <div className="rounded-xl border border-gray-100 bg-white p-6 shadow-lg">
      <div className="mb-6 flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
          Alertas Operacionales
          <span className="rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-800">
            {alertas.length}
          </span>
        </h2>
      </div>

      <div className="max-h-[500px] space-y-4 overflow-y-auto pr-2 custom-scrollbar">
        {alertas.map((alerta) => (
          <div
            key={alerta.id}
            className={`group rounded-xl border p-5 transition-all hover:shadow-md ${getCriticidadColor(alerta.nivel_criticidad)}`}
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex flex-1 items-start gap-4">
                <div className="mt-1">{getCriticidadIcon(alerta.nivel_criticidad)}</div>

                <div className="flex-1">
                  <div className="mb-2 flex items-center justify-between">
                    <span className="text-sm font-bold text-gray-900 uppercase tracking-tight">
                      {alerta.tipo_alerta}
                    </span>
                    <span className="text-xs font-medium text-gray-500 bg-white/50 px-2 py-1 rounded">
                      {new Date(alerta.fecha_generacion).toLocaleDateString('es-AR')}
                    </span>
                  </div>

                  <div className="space-y-2">
                    <div>
                      <p className="text-[10px] font-bold uppercase tracking-wider text-gray-400">
                        Análisis de Factores
                      </p>
                      <p className="text-sm leading-relaxed text-gray-700 font-medium">
                        {formatMensaje(alerta.mensaje)}
                      </p>
                    </div>

                    {alerta.aeropuertos && (
                      <div className="flex items-center gap-1 text-xs text-gray-600">
                        <MapPin className="h-3 w-3" />
                        <span>Aeropuerto: {alerta.aeropuertos.nombre}</span>
                      </div>
                    )}

                    {/* Score Predictivo con barra visual */}
                    {alerta.score_predictivo !== null && (
                      <div className="mt-3 pt-3 border-t border-black/5">
                         <div className="flex items-center justify-between mb-1">
                            <span className="text-[10px] font-bold text-gray-500 uppercase">Probabilidad de Incidente</span>
                            <span className="text-xs font-bold text-gray-700">{alerta.score_predictivo}%</span>
                         </div>
                         <div className="h-1.5 w-full rounded-full bg-gray-200">
                            <div 
                              className={`h-1.5 rounded-full transition-all ${alerta.score_predictivo > 70 ? 'bg-red-500' : 'bg-orange-400'}`} 
                              style={{ width: `${alerta.score_predictivo}%` }}
                            ></div>
                         </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              <button
                onClick={() => handleResolve(alerta.id)}
                disabled={processingId === alerta.id}
                className="flex items-center gap-1.5 self-center rounded-lg bg-green-600 px-4 py-2 text-xs font-bold text-white shadow-sm transition hover:bg-green-700 disabled:opacity-50"
              >
                {processingId === alerta.id ? (
                  '...'
                ) : (
                  <>
                    <CheckCircle className="h-4 w-4" />
                    Resolver
                  </>
                )}
              </button>
            </div>
          </div>
        ))}

        {alertas.length === 0 && (
          <div className="py-16 text-center">
            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-50">
              <CheckCircle className="h-10 w-10 text-green-500" />
            </div>
            <p className="text-lg font-semibold text-gray-900">Operación Segura</p>
            <p className="text-sm text-gray-500">No se han detectado alertas predictivas pendientes.</p>
          </div>
        )}
      </div>
    </div>
  );
}
