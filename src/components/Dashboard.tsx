import { useEffect, useState } from 'react';
import { supabase } from '../lib/supabase';
import { useAuth } from '../contexts/AuthContext';
import {
  AlertTriangle,
  TrendingUp,
  Plane,
  MapPin,
  Activity,
  LogOut,
  Menu,
  X
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

export default function Dashboard() {
  const { usuario, signOut } = useAuth();
  const [stats, setStats] = useState({
    totalIncidentes: 0,
    alertasActivas: 0,
    aeropuertos: 0,
    riesgoPromedio: 0
  });
  const [recentIncidentes, setRecentIncidentes] = useState<Incidente[]>([]);
  const [alertas, setAlertas] = useState<Alerta[]>([]);
  const [loading, setLoading] = useState(true);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);

  async function loadDashboardData() {
    try {
      const [incidentesRes, alertasRes, aeropuertosRes] = await Promise.all([
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
        supabase.from('aeropuertos').select('id', { count: 'exact', head: true })
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
        riesgoPromedio: 42
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
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition">
            <div className="flex items-center justify-between mb-4">
              <div className="bg-red-100 p-3 rounded-lg">
                <AlertTriangle className="w-6 h-6 text-red-600" />
              </div>
              <span className="text-2xl font-bold text-gray-900">{stats.totalIncidentes}</span>
            </div>
            <h3 className="text-sm font-medium text-gray-600">Total Incidentes</h3>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition">
            <div className="flex items-center justify-between mb-4">
              <div className="bg-orange-100 p-3 rounded-lg">
                <Activity className="w-6 h-6 text-orange-600" />
              </div>
              <span className="text-2xl font-bold text-gray-900">{stats.alertasActivas}</span>
            </div>
            <h3 className="text-sm font-medium text-gray-600">Alertas Activas</h3>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition">
            <div className="flex items-center justify-between mb-4">
              <div className="bg-blue-100 p-3 rounded-lg">
                <MapPin className="w-6 h-6 text-blue-600" />
              </div>
              <span className="text-2xl font-bold text-gray-900">{stats.aeropuertos}</span>
            </div>
            <h3 className="text-sm font-medium text-gray-600">Aeropuertos</h3>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition">
            <div className="flex items-center justify-between mb-4">
              <div className="bg-green-100 p-3 rounded-lg">
                <TrendingUp className="w-6 h-6 text-green-600" />
              </div>
              <span className="text-2xl font-bold text-gray-900">{stats.riesgoPromedio}%</span>
            </div>
            <h3 className="text-sm font-medium text-gray-600">Índice de Riesgo</h3>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Incidentes Recientes</h2>
            <div className="space-y-3">
              {recentIncidentes.map((incidente) => (
                <div key={incidente.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <p className="font-semibold text-gray-900">{incidente.tipos_incidente?.nombre || 'Sin tipo'}</p>
                      <p className="text-sm text-gray-600">{incidente.aeropuertos?.nombre || 'Sin aeropuerto'}</p>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getRiesgoColor(incidente.nivel_riesgo)}`}>
                      {incidente.nivel_riesgo || 'N/A'}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500">{new Date(incidente.fecha_hora).toLocaleString('es-ES')}</p>
                </div>
              ))}
              {recentIncidentes.length === 0 && (
                <p className="text-gray-500 text-center py-8">No hay incidentes recientes</p>
              )}
            </div>
          </div>

          <AlertasPanel alertas={alertas} onUpdate={loadDashboardData} />
        </div>

        <IncidentesTable onUpdate={loadDashboardData} />
      </div>
    </div>
  );
}
