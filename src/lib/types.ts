export type RolUsuario = 'administrador' | 'inspector' | 'analista' | 'supervisor';

export interface Usuario {
  id: string;
  nombre: string;
  email: string;
  rol: RolUsuario;
  estado: boolean;
  ultimo_login: string | null;
  created_at: string;
}

export interface AuthSession {
  access_token: string;
}

export interface Aeropuerto {
  id: number;
  codigo_iata: string | null;
  codigo_icao: string;
  nombre: string;
  ciudad: string | null;
  provincia: string | null;
  categoria: string | null;
  estado: string;
  latitud: number | null;
  longitud: number | null;
  created_at: string;
}

export interface TipoIncidente {
  id: number;
  codigo_oaci: string | null;
  nombre: string;
  categoria: string | null;
}

export interface Aeronave {
  id: number;
  matricula: string;
  modelo: string | null;
  fabricante: string | null;
  anio_fabricacion: number | null;
  operador: string | null;
  tipo_aeronave: string | null;
  peso_maximo_despegue: number | null;
  ultima_revision_mtto: string | null;
}

export type NivelRiesgo = 'Bajo' | 'Medio' | 'Alto' | 'Crítico';

export interface Incidente {
  id: number;
  aeropuerto_id: number | null;
  pista_id: number | null;
  aeronave_id: number | null;
  tipo_incidente_id: number | null;
  fecha_hora: string;
  descripcion: string | null;
  nivel_riesgo: NivelRiesgo | null;
  fase_vuelo: string | null;
  condicion_meteorologica: string | null;
  condicion_luz: string | null;
  visibilidad_millas: number | null;
  viento_kt: number | null;
  latitud: number | null;
  longitud: number | null;
  reportado_por: string | null;
  created_at: string;
  aeropuertos?: Pick<Aeropuerto, 'nombre' | 'codigo_icao'> | null;
  tipos_incidente?: Pick<TipoIncidente, 'nombre'> | null;
  aeronaves?: Pick<Aeronave, 'matricula'> | null;
}

export interface Alerta {
  id: number;
  aeropuerto_id: number | null;
  fecha_generacion: string;
  tipo_alerta: string | null;
  nivel_criticidad: string | null;
  mensaje: string | null;
  score_predictivo: number | null;
  ejecucion_agente_id: number | null;
  estado: string;
  atendido_por: string | null;
  fecha_resolucion: string | null;
  aeropuertos?: Pick<Aeropuerto, 'nombre'> | null;
}

export interface DashboardSummary {
  stats: {
    totalIncidentes: number;
    alertasActivas: number;
    aeropuertos: number;
    riesgoPromedio: number;
    riesgoFuturo: number;
  };
  recentIncidentes: Incidente[];
  alertas: Alerta[];
}

export interface FormCatalogs {
  aeropuertos: Aeropuerto[];
  tipos_incidente: TipoIncidente[];
  aeronaves: Aeronave[];
}

export interface ReporteTopItem {
  clave: string;
  total: number;
}

export interface ReporteEjecutivo {
  generado_en: string;
  periodo_dias: number;
  organismo_referencia: string;
  marco_regulatorio: string[];
  estado_modelo: {
    version: string;
    registros_entrenamiento: number;
    accuracy: number | null;
  };
  resumen_operacional: {
    incidentes_periodo: number;
    alertas_pendientes: number;
    alertas_resueltas_periodo: number;
    usuarios_activos: number;
    aeropuertos_monitoreados: number;
    riesgo_promedio: number;
    riesgo_futuro: number;
  };
  trazabilidad: {
    incidentes_con_clima: number;
    incidentes_con_geolocalizacion: number;
    incidentes_auditados: number;
    acciones_auditadas_periodo: number;
  };
  top_aeropuertos: ReporteTopItem[];
  top_tipos_incidente: ReporteTopItem[];
  distribucion_riesgo: ReporteTopItem[];
  recomendaciones: string[];
}

export interface FormTemplateField {
  id: number;
  clave: string;
  etiqueta: string;
  tipo_campo: string;
  requerido: boolean;
  opciones: string[];
  orden: number;
}

export interface FormTemplate {
  id: number;
  organization_key: string;
  nombre: string;
  modulo: string;
  version: number;
  estado: string;
  created_by: string | null;
  created_at: string;
  fields: FormTemplateField[];
}

export interface Inspeccion {
  id: number;
  organization_key: string;
  template_id: number | null;
  aeropuerto_id: number | null;
  titulo: string;
  alcance: string | null;
  estado: string;
  criticidad: string | null;
  fecha_programada: string | null;
  fecha_ejecucion: string | null;
  responsable_id: string | null;
  observaciones: string | null;
  created_at: string;
}

export interface AccionCorrectiva {
  id: number;
  organization_key: string;
  inspection_id: number | null;
  incidente_id: number | null;
  titulo: string;
  descripcion: string | null;
  prioridad: string;
  estado: string;
  fecha_vencimiento: string | null;
  responsable_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface CursoCapacitacion {
  id: number;
  organization_key: string;
  nombre: string;
  categoria: string | null;
  modalidad: string | null;
  vigencia_meses: number | null;
  obligatorio_para: string[];
  estado: string;
  created_at: string;
}

export interface RegistroCapacitacion {
  id: number;
  course_id: number;
  user_id: string | null;
  organization_key: string;
  estado: string;
  fecha_asignacion: string;
  fecha_completado: string | null;
  fecha_vencimiento: string | null;
  puntaje: number | null;
  observaciones: string | null;
  created_at: string;
}

export interface NotificacionOperativa {
  id: number;
  organization_key: string;
  canal: string;
  tipo: string;
  titulo: string;
  mensaje: string;
  severidad: string;
  estado: string;
  destinatario_user_id: string | null;
  recurso_tipo: string | null;
  recurso_id: string | null;
  sent_at: string | null;
  read_at: string | null;
  created_at: string;
}

export interface ExporteRegulatorio {
  generado_en: string;
  formato: string;
  nombre_archivo: string;
  contenido: string;
}

export interface ResultadoOperacionMasiva {
  eliminados: number;
  detalle: string;
}
