import { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import {
  AlertTriangle,
  TrendingUp,
  Plane,
  MapPin,
  Activity,
  LogOut
} from 'lucide-react';
import IncidentesTable from './IncidentesTable';
import AlertasPanel from './AlertasPanel';
import { api } from '../lib/api';
import type { Alerta, Incidente } from '../lib/types';
import { getPrediccionRiesgo, type PredictiveResult } from '../services/predictiveService';

type IncidentPrediction = PredictiveResult & {
  incidentId: number;
};

async function generarAlertasPredictivas() {
  const incidentes = await api.listIncidentes(20);
  if (!incidentes?.length) return;

  const alertasPendientes = await api.listAlertasPendientes(50);

  await Promise.all(
    incidentes.map(async (incidente) => {
      const pred = await getPrediccionRiesgo(incidente);

      if (pred.score <= 70) return;

      const resumenFactores = pred.factores?.slice(0, 2).join(', ');
      const mensaje = resumenFactores
        ? `Alto riesgo detectado en incidente ${incidente.id}. Factores: ${resumenFactores}.`
        : `Alto riesgo detectado en incidente ${incidente.id}`;
      const alertaExistente = alertasPendientes.find((alerta) =>
        alerta.tipo_alerta === 'Riesgo Predictivo' &&
        (alerta.mensaje || '').includes(`incidente ${incidente.id}`)
      );
      if (alertaExistente) return;

      await api.createAlerta({
        tipo_alerta: 'Riesgo Predictivo',
        mensaje,
        nivel_criticidad: pred.score > 85 ? 'Crítico' : 'Alta',
        estado: 'Pendiente',
        score_predictivo: pred.score,
        aeropuerto_id: incidente.aeropuerto_id
      });
    })
  );
}
export default function Dashboard() {
  const { usuario, signOut } = useAuth();

  const [stats, setStats] = useState({
  totalIncidentes: 0,
  alertasActivas: 0,
  aeropuertos: 0,
  riesgoPromedio: 0,
  riesgoFuturo: 0 
});
  const [recentIncidentes, setRecentIncidentes] = useState<Incidente[]>([]);
  const [alertas, setAlertas] = useState<Alerta[]>([]);
  const [incidentPredictions, setIncidentPredictions] = useState<Record<number, IncidentPrediction>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

async function loadDashboardData() {
  try {
    await generarAlertasPredictivas();
    const summary = await api.getDashboardSummary();
    const predictions = await Promise.all(
      summary.recentIncidentes.map(async (incidente) => ({
        incidentId: incidente.id,
        ...(await getPrediccionRiesgo(incidente)),
      }))
    );

    setRecentIncidentes(summary.recentIncidentes);
    setAlertas(summary.alertas);
    setStats(summary.stats);
    setIncidentPredictions(
      predictions.reduce<Record<number, IncidentPrediction>>((acc, prediction) => {
        acc[prediction.incidentId] = prediction;
        return acc;
      }, {})
    );

  } catch (error) {
      console.error('Error loading dashboard:', error);
  } finally {
    setLoading(false);
  }
}
  function getRiesgoColor(nivel: string | null) {
    switch (nivel) {
      case 'Crítico': return 'bg-red-100 text-red-800 border-red-300';
      case 'Alto': return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'Medio': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'Bajo': return 'bg-green-100 text-green-800 border-green-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-sky-50 via-blue-50 to-cyan-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Cargando datos...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-sky-50 via-blue-50 to-cyan-50">
      <nav className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <div className="bg-gradient-to-br from-sky-500 to-blue-600 p-2 rounded-lg mr-3">
                <Plane className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Sistema de Seguridad Aeronáutica</h1>
                <p className="text-xs text-gray-600">Plataforma Predictiva</p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="hidden md:block text-right">
                <p className="text-sm font-medium text-gray-900">{usuario?.nombre}</p>
                <p className="text-xs text-gray-600 capitalize">{usuario?.rol}</p>
              </div>
              <button
                onClick={() => signOut()}
                className="flex items-center space-x-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition"
              >
                <LogOut className="w-4 h-4" />
                <span className="hidden md:inline">Salir</span>
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

        {/* 🔥 STATS */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">

          <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
            <div className="flex justify-between mb-4">
              <AlertTriangle className="w-6 h-6 text-red-600" />
              <span className="text-2xl font-bold">{stats.totalIncidentes}</span>
            </div>
            <h3 className="text-sm text-gray-600">Total Incidentes</h3>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
            <div className="flex justify-between mb-4">
              <Activity className="w-6 h-6 text-orange-600" />
              <span className="text-2xl font-bold">{stats.alertasActivas}</span>
            </div>
            <h3 className="text-sm text-gray-600">Alertas Activas</h3>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
            <div className="flex justify-between mb-4">
              <MapPin className="w-6 h-6 text-blue-600" />
              <span className="text-2xl font-bold">{stats.aeropuertos}</span>
            </div>
            <h3 className="text-sm text-gray-600">Aeropuertos</h3>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
            <div className="flex justify-between mb-4">
              <TrendingUp className="w-6 h-6 text-green-600" />
              <span className="text-2xl font-bold">{stats.riesgoPromedio}%</span>
            </div>
            <h3 className="text-sm text-gray-600">Índice de Riesgo</h3>
          </div>

        </div>

        {/* 📊 CONTENIDO */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">

          <div className="bg-white rounded-xl shadow-lg border p-6">
            <h2 className="text-lg font-bold mb-4">Incidentes Recientes</h2>

            {recentIncidentes.map((incidente) => (
              <div key={incidente.id} className="border p-4 rounded-lg mb-3">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="font-semibold">{incidente.tipos_incidente?.nombre}</p>
                    <p className="text-sm text-gray-600">{incidente.aeropuertos?.nombre}</p>
                  </div>
                  {incidentPredictions[incidente.id] && (
                    <div className="text-right">
                      <p className="text-xs text-gray-500">Puntaje IA</p>
                      <p className="text-lg font-bold text-sky-700">{incidentPredictions[incidente.id].score}%</p>
                    </div>
                  )}
                </div>
                <span className={`text-xs px-2 py-1 rounded ${getRiesgoColor(incidente.nivel_riesgo)}`}>
                  {incidente.nivel_riesgo}
                </span>
                {incidentPredictions[incidente.id] && (
                  <div className="mt-3 rounded-lg bg-slate-50 border border-slate-200 p-3">
                    <div className="flex flex-wrap items-center gap-2 mb-2 text-xs">
                      <span className="px-2 py-1 rounded-full bg-sky-100 text-sky-700">
                        Modelo: {incidentPredictions[incidente.id].modelo || 'No disponible'}
                      </span>
                      <span className="px-2 py-1 rounded-full bg-gray-100 text-gray-700">
                        Origen: {incidentPredictions[incidente.id].fuente === 'api' ? 'Modelo productivo' : 'Respaldo local'}
                      </span>
                    </div>
                    <p className="text-xs font-semibold text-gray-700 mb-1">Factores principales</p>
                    <div className="flex flex-wrap gap-2">
                      {(incidentPredictions[incidente.id].factores?.slice(0, 3) || ['Sin factores disponibles']).map((factor) => (
                        <span
                          key={factor}
                          className="text-xs px-2 py-1 rounded-full bg-white border border-slate-200 text-slate-700"
                        >
                          {factor}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}

          </div>
           <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
                <div className="flex justify-between mb-4">
                   <TrendingUp className="w-6 h-6 text-purple-600" />
                    <span className="text-2xl font-bold">{stats.riesgoFuturo}%</span>
                </div>
              <h3 className="text-sm text-gray-600">Riesgo Próximas 24h</h3>
              <p className="mt-3 text-sm text-gray-600">
                Estimado con modelo entrenado en NTSB y variables meteorológicas reales.
              </p>
              <div className="mt-4 rounded-lg bg-sky-50 border border-sky-100 p-4">
                <p className="text-xs font-semibold text-sky-800 mb-2">Explicabilidad IA</p>
                <p className="text-sm text-sky-900">
                  El motor pondera narrativa del incidente, fase de vuelo, condiciones de luz, visibilidad,
                  viento, techo de nubes y otras señales operacionales para priorizar riesgo.
                </p>
              </div>
              <div className="mt-4 rounded-lg bg-emerald-50 border border-emerald-100 p-4">
                <p className="text-xs font-semibold text-emerald-800 mb-2">Motor predictivo desplegado</p>
                <p className="text-sm text-emerald-900">
                  Entrenado con 30.212 eventos oficiales de NTSB y precisión de validación cercana al 78%.
                </p>
              </div>
          </div>
          <AlertasPanel alertas={alertas} onUpdate={loadDashboardData} />

        </div>

        <IncidentesTable onUpdate={loadDashboardData} />

      </div>
    </div>
  );
}
