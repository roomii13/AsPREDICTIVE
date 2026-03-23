import { useEffect, useState } from 'react';
import { supabase } from '../lib/supabase';
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
import type { Database } from '../lib/database.types';

type Incidente = Database['public']['Tables']['incidentes']['Row'] & {
  aeropuertos?: { nombre: string; codigo_icao: string } | null;
  tipos_incidente?: { nombre: string } | null;
};

type Alerta = Database['public']['Tables']['alertas']['Row'] & {
  aeropuertos?: { nombre: string } | null;
};

// ✅ Cálculo real del riesgo promedio
async function calcularRiesgoPromedio() {
  const { data } = await supabase
    .from('incidentes')
    .select('nivel_riesgo');

  if (!data || data.length === 0) return 0;

  const map: any = { Bajo: 1, Medio: 2, Alto: 3, Crítico: 4 };

  const promedio =
    data.reduce((acc: number, curr: any) => acc + (map[curr.nivel_riesgo] || 0), 0) /
    data.length;

  return Math.round((promedio / 4) * 100);
}


async function predecirRiesgoFuturo() {
  const { data } = await supabase
    .from('incidentes')
    .select('*')
    .order('fecha_hora', { ascending: false })
    .limit(20);

  if (!data || data.length === 0) return 0;

  // Simulación de tendencia (colocar IA real)
  const map: any = { Bajo: 1, Medio: 2, Alto: 3, Crítico: 4 };

  const tendencia =
    data.reduce((acc: number, curr: any) => acc + (map[curr.nivel_riesgo] || 0), 0) /
    data.length;

  // Simula aumento de riesgo futuro
  const prediccion = tendencia * (1 + Math.random() * 0.3);

  return Math.min(100, Math.round((prediccion / 4) * 100));
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
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

async function loadDashboardData() {
  try {
    const [incidentesRes, alertasRes, aeropuertosRes, riesgoPromedio, riesgoFuturo] = await Promise.all([
      supabase
        .from('incidentes')
        .select('*, aeropuertos(nombre, codigo_icao), tipos_incidente(nombre)')
        .order('fecha_hora', { ascending: false })
        .limit(5),

      supabase
        .from('alertas')
        .select('*, aeropuertos(nombre)')
        .eq('estado', 'Pendiente')
        .order('fecha_generacion', { ascending: false })
        .limit(10),

      supabase.from('aeropuertos').select('id', { count: 'exact', head: true }),

      calcularRiesgoPromedio(),
      predecirRiesgoFuturo()
    ]);

    if (incidentesRes.data) setRecentIncidentes(incidentesRes.data);
    if (alertasRes.data) setAlertas(alertasRes.data);

    const { count: totalIncidentes } = await supabase
      .from('incidentes')
      .select('*', { count: 'exact', head: true });

    setStats({
      totalIncidentes: totalIncidentes || 0,
      alertasActivas: alertasRes.data?.length || 0,
      aeropuertos: aeropuertosRes.count || 0,
      riesgoPromedio,
      riesgoFuturo
    });

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
              <div key={incidente.id} className="border p-4 rounded-lg mb-2">
                <p className="font-semibold">{incidente.tipos_incidente?.nombre}</p>
                <p className="text-sm text-gray-600">{incidente.aeropuertos?.nombre}</p>
                <span className={`text-xs px-2 py-1 rounded ${getRiesgoColor(incidente.nivel_riesgo)}`}>
                  {incidente.nivel_riesgo}
                </span>
              </div>
            ))}

          </div>
           <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
                <div className="flex justify-between mb-4">
                   <TrendingUp className="w-6 h-6 text-purple-600" />
                    <span className="text-2xl font-bold">{stats.riesgoFuturo}%</span>
                </div>
              <h3 className="text-sm text-gray-600">Riesgo Próximas 24h</h3>
          </div>
          <AlertasPanel alertas={alertas} onUpdate={loadDashboardData} />

        </div>

        <IncidentesTable onUpdate={loadDashboardData} />

      </div>
    </div>
  );
}
