import type {
  Aeropuerto,
  Aeronave,
  Alerta,
  AuthSession,
  DashboardSummary,
  FormCatalogs,
  Incidente,
  Inspeccion,
  NivelRiesgo,
  NotificacionOperativa,
  ReporteEjecutivo,
  ExporteRegulatorio,
  ResultadoOperacionMasiva,
  AccionCorrectiva,
  CursoCapacitacion,
  FormTemplate,
  RegistroCapacitacion,
  RolUsuario,
  TipoIncidente,
  Usuario,
} from './types';

const apiBaseUrl = import.meta.env.VITE_API_URL?.replace(/\/$/, '') || 'http://localhost:8000';
const TOKEN_KEY = 'aviation_auth_token';

type RequestOptions = RequestInit & {
  auth?: boolean;
};

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function buildHeaders(initHeaders?: HeadersInit, auth = true) {
  const headers = new Headers(initHeaders);
  headers.set('Content-Type', 'application/json');

  if (auth) {
    const token = getToken();
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }
  }

  return headers;
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...options,
    headers: buildHeaders(options.headers, options.auth !== false),
  });

  if (!response.ok) {
    let message = 'Error inesperado en la API';
    try {
      const errorBody = await response.json();
      message = errorBody.detail || errorBody.message || message;
    } catch {
      message = response.statusText || message;
    }
    throw new Error(message);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export const api = {
  getBaseUrl() {
    return apiBaseUrl;
  },
  setToken(token: string) {
    localStorage.setItem(TOKEN_KEY, token);
  },
  clearToken() {
    localStorage.removeItem(TOKEN_KEY);
  },
  getToken,
  async signIn(email: string, password: string) {
    return request<{ access_token: string; user: Usuario }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
      auth: false,
    });
  },
  async signUp(email: string, password: string, nombre: string, rol: RolUsuario) {
    return request<{ access_token: string; user: Usuario }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, nombre, rol }),
      auth: false,
    });
  },
  async getMe() {
    return request<Usuario>('/auth/me');
  },
  async getDashboardSummary() {
    return request<DashboardSummary>('/dashboard/summary');
  },
  async getFormCatalogs() {
    return request<FormCatalogs>('/catalogs/form-data');
  },
  async listIncidentes(limit = 50) {
    return request<Incidente[]>(`/incidentes?limit=${limit}`);
  },
  async createIncidente(payload: {
    aeropuerto_id: number | null;
    tipo_incidente_id: number | null;
    aeronave_id: number | null;
    fecha_hora: string;
    descripcion: string;
    nivel_riesgo: NivelRiesgo;
    fase_vuelo: string;
    condicion_meteorologica?: string | null;
    condicion_luz?: string | null;
    visibilidad_millas?: number | null;
    viento_kt?: number | null;
    latitud: number | null;
    longitud: number | null;
  }) {
    return request<Incidente>('/incidentes', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },
  async updateIncidente(id: number, payload: {
    aeropuerto_id: number | null;
    tipo_incidente_id: number | null;
    aeronave_id: number | null;
    fecha_hora: string;
    descripcion: string;
    nivel_riesgo: NivelRiesgo;
    fase_vuelo: string;
    condicion_meteorologica?: string | null;
    condicion_luz?: string | null;
    visibilidad_millas?: number | null;
    viento_kt?: number | null;
    latitud: number | null;
    longitud: number | null;
  }) {
    return request<Incidente>(`/incidentes/${id}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    });
  },
  async listAlertasPendientes(limit = 10) {
    return request<Alerta[]>(`/alertas?estado=Pendiente&limit=${limit}`);
  },
  async createAlerta(payload: {
    aeropuerto_id: number | null;
    tipo_alerta: string;
    nivel_criticidad: string;
    mensaje: string;
    score_predictivo: number | null;
    estado?: string;
  }) {
    return request<Alerta>('/alertas', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },
  async resolveAlerta(alertaId: number) {
    return request<Alerta>(`/alertas/${alertaId}/resolve`, {
      method: 'POST',
      body: JSON.stringify({}),
    });
  },
  async countAeropuertos() {
    return request<{ total: number }>('/catalogs/aeropuertos/count');
  },
  async listAeropuertos() {
    return request<Aeropuerto[]>('/catalogs/aeropuertos');
  },
  async listTiposIncidente() {
    return request<TipoIncidente[]>('/catalogs/tipos-incidente');
  },
  async listAeronaves() {
    return request<Aeronave[]>('/catalogs/aeronaves');
  },
  async getReporteEjecutivo(periodoDias = 90) {
    return request<ReporteEjecutivo>(`/reports/executive?periodo_dias=${periodoDias}`);
  },
  async listFormTemplates(organizationKey = 'default') {
    return request<FormTemplate[]>(`/institutional/form-templates?organization_key=${organizationKey}`);
  },
  async createFormTemplate(payload: {
    organization_key: string;
    nombre: string;
    modulo: string;
    version?: number;
    estado?: string;
    fields?: Array<{
      clave: string;
      etiqueta: string;
      tipo_campo: string;
      requerido?: boolean;
      opciones?: string[];
      orden?: number;
    }>;
  }) {
    return request<FormTemplate>('/institutional/form-templates', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },
  async listInspections(organizationKey = 'default') {
    return request<Inspeccion[]>(`/institutional/inspections?organization_key=${organizationKey}`);
  },
  async createInspection(payload: {
    organization_key: string;
    template_id?: number | null;
    aeropuerto_id?: number | null;
    titulo: string;
    alcance?: string | null;
    estado?: string;
    criticidad?: string | null;
    fecha_programada?: string | null;
    observaciones?: string | null;
  }) {
    return request<Inspeccion>('/institutional/inspections', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },
  async deleteInspection(inspectionId: number) {
    return request<void>(`/institutional/inspections/${inspectionId}`, {
      method: 'DELETE',
    });
  },
  async deleteTestInspections(title = 'auditoria', organizationKey = 'default') {
    return request<ResultadoOperacionMasiva>(
      `/institutional/inspections?organization_key=${organizationKey}&title=${encodeURIComponent(title)}&only_pending=true`,
      {
        method: 'DELETE',
      },
    );
  },
  async listCorrectiveActions(organizationKey = 'default') {
    return request<AccionCorrectiva[]>(`/institutional/corrective-actions?organization_key=${organizationKey}`);
  },
  async createCorrectiveAction(payload: {
    organization_key: string;
    inspection_id?: number | null;
    incidente_id?: number | null;
    titulo: string;
    descripcion?: string | null;
    prioridad?: string;
    estado?: string;
    fecha_vencimiento?: string | null;
  }) {
    return request<AccionCorrectiva>('/institutional/corrective-actions', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },
  async updateCorrectiveActionStatus(actionId: number, estado: string) {
    return request<AccionCorrectiva>(`/institutional/corrective-actions/${actionId}/status`, {
      method: 'POST',
      body: JSON.stringify({ estado }),
    });
  },
  async listTrainingCourses(organizationKey = 'default') {
    return request<CursoCapacitacion[]>(`/institutional/training/courses?organization_key=${organizationKey}`);
  },
  async createTrainingCourse(payload: {
    organization_key: string;
    nombre: string;
    categoria?: string | null;
    modalidad?: string | null;
    vigencia_meses?: number | null;
    obligatorio_para?: string[];
    estado?: string;
  }) {
    return request<CursoCapacitacion>('/institutional/training/courses', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },
  async listTrainingRecords(organizationKey = 'default') {
    return request<RegistroCapacitacion[]>(`/institutional/training/records?organization_key=${organizationKey}`);
  },
  async createTrainingRecord(payload: {
    organization_key: string;
    course_id: number;
    user_id?: string | null;
    estado?: string;
    fecha_vencimiento?: string | null;
    observaciones?: string | null;
  }) {
    return request<RegistroCapacitacion>('/institutional/training/records', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },
  async completeTrainingRecord(recordId: number, puntaje?: number | null, observaciones?: string | null) {
    return request<RegistroCapacitacion>(`/institutional/training/records/${recordId}/complete`, {
      method: 'POST',
      body: JSON.stringify({ puntaje, observaciones }),
    });
  },
  async listNotifications(organizationKey = 'default') {
    return request<NotificacionOperativa[]>(`/institutional/notifications?organization_key=${organizationKey}`);
  },
  async markNotificationRead(notificationId: number, estado = 'Leida') {
    return request<NotificacionOperativa>(`/institutional/notifications/${notificationId}/read`, {
      method: 'POST',
      body: JSON.stringify({ estado }),
    });
  },
  async getRegulatoryExport(organizationKey = 'default') {
    return request<ExporteRegulatorio>(`/institutional/exports/regulatory?organization_key=${organizationKey}`);
  },
};
