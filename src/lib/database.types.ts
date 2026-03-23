export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[];

export interface Database {
  public: {
    Tables: {
      usuarios: {
        Row: {
          id: string;
          auth_user_id: string | null;
          nombre: string;
          email: string;
          rol: 'administrador' | 'inspector' | 'analista' | 'supervisor';
          estado: boolean;
          ultimo_login: string | null;
          created_at: string;
        };
        Insert: {
          id?: string;
          auth_user_id?: string | null;
          nombre: string;
          email: string;
          rol: 'administrador' | 'inspector' | 'analista' | 'supervisor';
          estado?: boolean;
          ultimo_login?: string | null;
          created_at?: string;
        };
        Update: {
          id?: string;
          auth_user_id?: string | null;
          nombre?: string;
          email?: string;
          rol?: 'administrador' | 'inspector' | 'analista' | 'supervisor';
          estado?: boolean;
          ultimo_login?: string | null;
          created_at?: string;
        };
      };
      aeropuertos: {
        Row: {
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
        };
        Insert: {
          id?: number;
          codigo_iata?: string | null;
          codigo_icao: string;
          nombre: string;
          ciudad?: string | null;
          provincia?: string | null;
          categoria?: string | null;
          estado?: string;
          latitud?: number | null;
          longitud?: number | null;
          created_at?: string;
        };
        Update: {
          id?: number;
          codigo_iata?: string | null;
          codigo_icao?: string;
          nombre?: string;
          ciudad?: string | null;
          provincia?: string | null;
          categoria?: string | null;
          estado?: string;
          latitud?: number | null;
          longitud?: number | null;
          created_at?: string;
        };
      };
      pistas: {
        Row: {
          id: number;
          aeropuerto_id: number | null;
          identificador: string;
          longitud_metros: number | null;
          ancho_metros: number | null;
          superficie: string | null;
          estado: string | null;
        };
        Insert: {
          id?: number;
          aeropuerto_id?: number | null;
          identificador: string;
          longitud_metros?: number | null;
          ancho_metros?: number | null;
          superficie?: string | null;
          estado?: string | null;
        };
        Update: {
          id?: number;
          aeropuerto_id?: number | null;
          identificador?: string;
          longitud_metros?: number | null;
          ancho_metros?: number | null;
          superficie?: string | null;
          estado?: string | null;
        };
      };
      aeronaves: {
        Row: {
          id: number;
          matricula: string;
          modelo: string | null;
          fabricante: string | null;
          anio_fabricacion: number | null;
          operador: string | null;
          tipo_aeronave: string | null;
          peso_maximo_despegue: number | null;
          ultima_revision_mtto: string | null;
        };
        Insert: {
          id?: number;
          matricula: string;
          modelo?: string | null;
          fabricante?: string | null;
          anio_fabricacion?: number | null;
          operador?: string | null;
          tipo_aeronave?: string | null;
          peso_maximo_despegue?: number | null;
          ultima_revision_mtto?: string | null;
        };
        Update: {
          id?: number;
          matricula?: string;
          modelo?: string | null;
          fabricante?: string | null;
          anio_fabricacion?: number | null;
          operador?: string | null;
          tipo_aeronave?: string | null;
          peso_maximo_despegue?: number | null;
          ultima_revision_mtto?: string | null;
        };
      };
      tipos_incidente: {
        Row: {
          id: number;
          codigo_oaci: string | null;
          nombre: string;
          categoria: string | null;
        };
        Insert: {
          id?: number;
          codigo_oaci?: string | null;
          nombre: string;
          categoria?: string | null;
        };
        Update: {
          id?: number;
          codigo_oaci?: string | null;
          nombre?: string;
          categoria?: string | null;
        };
      };
      incidentes: {
        Row: {
          id: number;
          aeropuerto_id: number | null;
          pista_id: number | null;
          aeronave_id: number | null;
          tipo_incidente_id: number | null;
          fecha_hora: string;
          descripcion: string | null;
          nivel_riesgo: 'Bajo' | 'Medio' | 'Alto' | 'Crítico' | null;
          fase_vuelo: string | null;
          latitud: number | null;
          longitud: number | null;
          reportado_por: string | null;
          created_at: string;
        };
        Insert: {
          id?: number;
          aeropuerto_id?: number | null;
          pista_id?: number | null;
          aeronave_id?: number | null;
          tipo_incidente_id?: number | null;
          fecha_hora: string;
          descripcion?: string | null;
          nivel_riesgo?: 'Bajo' | 'Medio' | 'Alto' | 'Crítico' | null;
          fase_vuelo?: string | null;
          latitud?: number | null;
          longitud?: number | null;
          reportado_por?: string | null;
          created_at?: string;
        };
        Update: {
          id?: number;
          aeropuerto_id?: number | null;
          pista_id?: number | null;
          aeronave_id?: number | null;
          tipo_incidente_id?: number | null;
          fecha_hora?: string;
          descripcion?: string | null;
          nivel_riesgo?: 'Bajo' | 'Medio' | 'Alto' | 'Crítico' | null;
          fase_vuelo?: string | null;
          latitud?: number | null;
          longitud?: number | null;
          reportado_por?: string | null;
          created_at?: string;
        };
      };
      alertas: {
        Row: {
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
        };
        Insert: {
          id?: number;
          aeropuerto_id?: number | null;
          fecha_generacion?: string;
          tipo_alerta?: string | null;
          nivel_criticidad?: string | null;
          mensaje?: string | null;
          score_predictivo?: number | null;
          ejecucion_agente_id?: number | null;
          estado?: string;
          atendido_por?: string | null;
          fecha_resolucion?: string | null;
        };
        Update: {
          id?: number;
          aeropuerto_id?: number | null;
          fecha_generacion?: string;
          tipo_alerta?: string | null;
          nivel_criticidad?: string | null;
          mensaje?: string | null;
          score_predictivo?: number | null;
          ejecucion_agente_id?: number | null;
          estado?: string;
          atendido_por?: string | null;
          fecha_resolucion?: string | null;
        };
      };
      reportes_seguridad: {
        Row: {
          id: number;
          aeropuerto_id: number | null;
          fecha: string;
          descripcion: string | null;
          anonimo: boolean;
          nivel_riesgo: string | null;
          estado_revision: string;
          reportado_por: string | null;
        };
        Insert: {
          id?: number;
          aeropuerto_id?: number | null;
          fecha?: string;
          descripcion?: string | null;
          anonimo?: boolean;
          nivel_riesgo?: string | null;
          estado_revision?: string;
          reportado_por?: string | null;
        };
        Update: {
          id?: number;
          aeropuerto_id?: number | null;
          fecha?: string;
          descripcion?: string | null;
          anonimo?: boolean;
          nivel_riesgo?: string | null;
          estado_revision?: string;
          reportado_por?: string | null;
        };
      };
      agentes_openfang: {
        Row: {
          id: number;
          nombre: string;
          descripcion: string | null;
          tipo_agente: string | null;
          capabilities: string[] | null;
          estado: string;
          frecuencia_ejecucion: string | null;
          version_modelo: string | null;
          created_at: string;
        };
        Insert: {
          id?: number;
          nombre: string;
          descripcion?: string | null;
          tipo_agente?: string | null;
          capabilities?: string[] | null;
          estado?: string;
          frecuencia_ejecucion?: string | null;
          version_modelo?: string | null;
          created_at?: string;
        };
        Update: {
          id?: number;
          nombre?: string;
          descripcion?: string | null;
          tipo_agente?: string | null;
          capabilities?: string[] | null;
          estado?: string;
          frecuencia_ejecucion?: string | null;
          version_modelo?: string | null;
          created_at?: string;
        };
      };
      historial_riesgo_diario: {
        Row: {
          id: number;
          aeropuerto_id: number | null;
          fecha: string;
          indice_riesgo: number | null;
          total_incidentes: number;
          total_reportes: number;
          clima_severo: boolean;
        };
        Insert: {
          id?: number;
          aeropuerto_id?: number | null;
          fecha: string;
          indice_riesgo?: number | null;
          total_incidentes?: number;
          total_reportes?: number;
          clima_severo?: boolean;
        };
        Update: {
          id?: number;
          aeropuerto_id?: number | null;
          fecha?: string;
          indice_riesgo?: number | null;
          total_incidentes?: number;
          total_reportes?: number;
          clima_severo?: boolean;
        };
      };
    };
    Views: {
      [_ in never]: never;
    };
    Functions: {
      [_ in never]: never;
    };
    Enums: {
      [_ in never]: never;
    };
  };
}
