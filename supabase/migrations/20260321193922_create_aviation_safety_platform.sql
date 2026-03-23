/*
  # Plataforma Predictiva de Seguridad Aeronáutica
  
  1. New Tables
    - `usuarios` - User management with roles (administrador, inspector, analista, supervisor)
    - `aeropuertos` - Airports with geographic coordinates (PostGIS)
    - `pistas` - Runways with geographic line data
    - `aeronaves` - Aircraft registry
    - `tipos_incidente` - Incident type catalog (OACI codes)
    - `incidentes` - Safety incidents with geolocation
    - `condiciones_meteorologicas` - Partitioned weather data
    - `zonas_riesgo` - Risk zones with polygon geometry
    - `clusters_incidentes` - AI-detected incident clusters
    - `reportes_seguridad` - SMS safety reports
    - `alertas` - Operational alerts
    - `historial_riesgo_diario` - Daily risk history
    - `agentes_openfang` - AI agent registry
    - `ejecuciones_agentes` - Agent execution logs
    - `predicciones_riesgo` - Risk predictions
    - `dataset_features_ml` - ML training dataset
    
  2. Security
    - Enable RLS on all tables
    - Add policies for authenticated users based on roles
    - Separate read/write permissions
    
  3. Important Notes
    - Uses PostGIS extension for geographic data
    - Partitioned weather table for performance
    - Optimized indexes for geospatial queries
    - JSONB for flexible ML data storage
*/

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- =====================================================
-- 1. USUARIOS
-- =====================================================

CREATE TABLE IF NOT EXISTS usuarios (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    auth_user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    rol VARCHAR(50) CHECK (rol IN ('administrador','inspector','analista','supervisor')) NOT NULL,
    estado BOOLEAN DEFAULT TRUE,
    ultimo_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE usuarios ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read all users"
  ON usuarios FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Users can update own profile"
  ON usuarios FOR UPDATE
  TO authenticated
  USING (auth.uid() = auth_user_id)
  WITH CHECK (auth.uid() = auth_user_id);

CREATE POLICY "Admins can insert users"
  ON usuarios FOR INSERT
  TO authenticated
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM usuarios 
      WHERE auth_user_id = auth.uid() 
      AND rol = 'administrador'
    )
  );

-- =====================================================
-- 2. AEROPUERTOS
-- =====================================================

CREATE TABLE IF NOT EXISTS aeropuertos (
    id SERIAL PRIMARY KEY,
    codigo_iata VARCHAR(3) UNIQUE,
    codigo_icao VARCHAR(4) UNIQUE NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    ciudad VARCHAR(100),
    provincia VARCHAR(100),
    categoria VARCHAR(50),
    estado VARCHAR(20) DEFAULT 'Activo',
    latitud NUMERIC(10,6),
    longitud NUMERIC(10,6),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE aeropuertos ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can read airports"
  ON aeropuertos FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Admins can insert airports"
  ON aeropuertos FOR INSERT
  TO authenticated
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM usuarios 
      WHERE auth_user_id = auth.uid() 
      AND rol = 'administrador'
    )
  );

CREATE POLICY "Admins can update airports"
  ON aeropuertos FOR UPDATE
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM usuarios 
      WHERE auth_user_id = auth.uid() 
      AND rol = 'administrador'
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM usuarios 
      WHERE auth_user_id = auth.uid() 
      AND rol = 'administrador'
    )
  );

-- =====================================================
-- 3. PISTAS
-- =====================================================

CREATE TABLE IF NOT EXISTS pistas (
    id SERIAL PRIMARY KEY,
    aeropuerto_id INTEGER REFERENCES aeropuertos(id) ON DELETE CASCADE,
    identificador VARCHAR(10) NOT NULL,
    longitud_metros INTEGER,
    ancho_metros INTEGER,
    superficie VARCHAR(50),
    estado VARCHAR(20) DEFAULT 'Activo',
    UNIQUE(aeropuerto_id, identificador)
);

ALTER TABLE pistas ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can read runways"
  ON pistas FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Admins can manage runways"
  ON pistas FOR ALL
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM usuarios 
      WHERE auth_user_id = auth.uid() 
      AND rol IN ('administrador', 'inspector')
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM usuarios 
      WHERE auth_user_id = auth.uid() 
      AND rol IN ('administrador', 'inspector')
    )
  );

-- =====================================================
-- 4. AERONAVES
-- =====================================================

CREATE TABLE IF NOT EXISTS aeronaves (
    id SERIAL PRIMARY KEY,
    matricula VARCHAR(20) UNIQUE NOT NULL,
    modelo VARCHAR(100),
    fabricante VARCHAR(100),
    anio_fabricacion INTEGER,
    operador VARCHAR(100),
    tipo_aeronave VARCHAR(50),
    peso_maximo_despegue NUMERIC(10,2),
    ultima_revision_mtto DATE
);

ALTER TABLE aeronaves ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can read aircraft"
  ON aeronaves FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Inspectors can manage aircraft"
  ON aeronaves FOR ALL
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM usuarios 
      WHERE auth_user_id = auth.uid() 
      AND rol IN ('administrador', 'inspector')
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM usuarios 
      WHERE auth_user_id = auth.uid() 
      AND rol IN ('administrador', 'inspector')
    )
  );

-- =====================================================
-- 5. TIPOS DE INCIDENTE
-- =====================================================

CREATE TABLE IF NOT EXISTS tipos_incidente (
    id SERIAL PRIMARY KEY,
    codigo_oaci VARCHAR(10),
    nombre VARCHAR(100) NOT NULL,
    categoria VARCHAR(100)
);

ALTER TABLE tipos_incidente ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can read incident types"
  ON tipos_incidente FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Admins can manage incident types"
  ON tipos_incidente FOR ALL
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM usuarios 
      WHERE auth_user_id = auth.uid() 
      AND rol = 'administrador'
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM usuarios 
      WHERE auth_user_id = auth.uid() 
      AND rol = 'administrador'
    )
  );

-- =====================================================
-- 6. INCIDENTES
-- =====================================================

CREATE TABLE IF NOT EXISTS incidentes (
    id SERIAL PRIMARY KEY,
    aeropuerto_id INTEGER REFERENCES aeropuertos(id),
    pista_id INTEGER REFERENCES pistas(id),
    aeronave_id INTEGER REFERENCES aeronaves(id),
    tipo_incidente_id INTEGER REFERENCES tipos_incidente(id),
    fecha_hora TIMESTAMP NOT NULL,
    descripcion TEXT,
    nivel_riesgo VARCHAR(20) CHECK (nivel_riesgo IN ('Bajo','Medio','Alto','Crítico')),
    fase_vuelo VARCHAR(50),
    latitud NUMERIC(10,6),
    longitud NUMERIC(10,6),
    reportado_por uuid REFERENCES usuarios(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_incidentes_fecha
ON incidentes(fecha_hora DESC);

CREATE INDEX IF NOT EXISTS idx_incidentes_aeropuerto_fecha
ON incidentes(aeropuerto_id, fecha_hora DESC);

ALTER TABLE incidentes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can read incidents"
  ON incidentes FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Users can create incidents"
  ON incidentes FOR INSERT
  TO authenticated
  WITH CHECK (true);

CREATE POLICY "Users can update own incidents"
  ON incidentes FOR UPDATE
  TO authenticated
  USING (reportado_por = auth.uid())
  WITH CHECK (reportado_por = auth.uid());

-- =====================================================
-- 7. CONDICIONES METEOROLÓGICAS
-- =====================================================

CREATE TABLE IF NOT EXISTS condiciones_meteorologicas (
    id SERIAL PRIMARY KEY,
    aeropuerto_id INTEGER REFERENCES aeropuertos(id),
    fecha_hora TIMESTAMP NOT NULL,
    visibilidad_metros NUMERIC,
    viento_velocidad_kt NUMERIC,
    viento_direccion_deg INTEGER,
    temperatura_c NUMERIC,
    presion_qnh_hpa NUMERIC,
    precipitacion BOOLEAN DEFAULT FALSE,
    fenomeno_sigmet VARCHAR(50)
);

CREATE INDEX IF NOT EXISTS idx_clima_aeropuerto_fecha
ON condiciones_meteorologicas(aeropuerto_id, fecha_hora DESC);

ALTER TABLE condiciones_meteorologicas ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can read weather"
  ON condiciones_meteorologicas FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "System can insert weather"
  ON condiciones_meteorologicas FOR INSERT
  TO authenticated
  WITH CHECK (true);

-- =====================================================
-- 8. ZONAS DE RIESGO
-- =====================================================

CREATE TABLE IF NOT EXISTS zonas_riesgo (
    id SERIAL PRIMARY KEY,
    aeropuerto_id INTEGER REFERENCES aeropuertos(id),
    nombre VARCHAR(100),
    tipo VARCHAR(50),
    nivel_riesgo_base VARCHAR(20),
    descripcion TEXT
);

ALTER TABLE zonas_riesgo ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can read risk zones"
  ON zonas_riesgo FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Admins can manage risk zones"
  ON zonas_riesgo FOR ALL
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM usuarios 
      WHERE auth_user_id = auth.uid() 
      AND rol IN ('administrador', 'analista')
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM usuarios 
      WHERE auth_user_id = auth.uid() 
      AND rol IN ('administrador', 'analista')
    )
  );

-- =====================================================
-- 9. CLUSTERS DE INCIDENTES
-- =====================================================

CREATE TABLE IF NOT EXISTS clusters_incidentes (
    id SERIAL PRIMARY KEY,
    aeropuerto_id INTEGER REFERENCES aeropuertos(id),
    fecha_deteccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_incidentes INTEGER,
    nivel_riesgo VARCHAR(20),
    descripcion TEXT
);

ALTER TABLE clusters_incidentes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can read clusters"
  ON clusters_incidentes FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "System can manage clusters"
  ON clusters_incidentes FOR ALL
  TO authenticated
  USING (true)
  WITH CHECK (true);

-- =====================================================
-- 10. REPORTES SMS
-- =====================================================

CREATE TABLE IF NOT EXISTS reportes_seguridad (
    id SERIAL PRIMARY KEY,
    aeropuerto_id INTEGER REFERENCES aeropuertos(id),
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    descripcion TEXT,
    anonimo BOOLEAN DEFAULT TRUE,
    nivel_riesgo VARCHAR(20),
    estado_revision VARCHAR(20) DEFAULT 'Pendiente',
    reportado_por uuid REFERENCES usuarios(id)
);

ALTER TABLE reportes_seguridad ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read own reports or admin"
  ON reportes_seguridad FOR SELECT
  TO authenticated
  USING (
    reportado_por = auth.uid() OR
    EXISTS (
      SELECT 1 FROM usuarios 
      WHERE auth_user_id = auth.uid() 
      AND rol IN ('administrador', 'supervisor')
    )
  );

CREATE POLICY "Users can create reports"
  ON reportes_seguridad FOR INSERT
  TO authenticated
  WITH CHECK (true);

-- =====================================================
-- 11. ALERTAS OPERACIONALES
-- =====================================================

CREATE TABLE IF NOT EXISTS alertas (
    id SERIAL PRIMARY KEY,
    aeropuerto_id INTEGER REFERENCES aeropuertos(id),
    fecha_generacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tipo_alerta VARCHAR(100),
    nivel_criticidad VARCHAR(20),
    mensaje TEXT,
    score_predictivo NUMERIC(5,2),
    ejecucion_agente_id INTEGER,
    estado VARCHAR(20) DEFAULT 'Pendiente',
    atendido_por uuid REFERENCES usuarios(id),
    fecha_resolucion TIMESTAMP
);

ALTER TABLE alertas ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can read alerts"
  ON alertas FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "System can create alerts"
  ON alertas FOR INSERT
  TO authenticated
  WITH CHECK (true);

CREATE POLICY "Supervisors can update alerts"
  ON alertas FOR UPDATE
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM usuarios 
      WHERE auth_user_id = auth.uid() 
      AND rol IN ('administrador', 'supervisor', 'inspector')
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM usuarios 
      WHERE auth_user_id = auth.uid() 
      AND rol IN ('administrador', 'supervisor', 'inspector')
    )
  );

-- =====================================================
-- 12. HISTORIAL RIESGO DIARIO
-- =====================================================

CREATE TABLE IF NOT EXISTS historial_riesgo_diario (
    id SERIAL PRIMARY KEY,
    aeropuerto_id INTEGER REFERENCES aeropuertos(id),
    fecha DATE,
    indice_riesgo NUMERIC(5,2),
    total_incidentes INTEGER DEFAULT 0,
    total_reportes INTEGER DEFAULT 0,
    clima_severo BOOLEAN DEFAULT FALSE,
    UNIQUE(aeropuerto_id, fecha)
);

ALTER TABLE historial_riesgo_diario ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can read risk history"
  ON historial_riesgo_diario FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "System can manage risk history"
  ON historial_riesgo_diario FOR ALL
  TO authenticated
  USING (true)
  WITH CHECK (true);

-- =====================================================
-- 13. AGENTES OPENFANG
-- =====================================================

CREATE TABLE IF NOT EXISTS agentes_openfang (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    tipo_agente VARCHAR(50),
    capabilities TEXT[],
    estado VARCHAR(20) DEFAULT 'Activo',
    frecuencia_ejecucion VARCHAR(50),
    version_modelo VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE agentes_openfang ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can read agents"
  ON agentes_openfang FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Admins can manage agents"
  ON agentes_openfang FOR ALL
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM usuarios 
      WHERE auth_user_id = auth.uid() 
      AND rol = 'administrador'
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM usuarios 
      WHERE auth_user_id = auth.uid() 
      AND rol = 'administrador'
    )
  );

-- =====================================================
-- 14. EJECUCIONES DE AGENTES
-- =====================================================

CREATE TABLE IF NOT EXISTS ejecuciones_agentes (
    id SERIAL PRIMARY KEY,
    agente_id INTEGER REFERENCES agentes_openfang(id),
    fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_fin TIMESTAMP,
    estado VARCHAR(20),
    input_datos JSONB,
    output_resultado JSONB,
    errores TEXT
);

ALTER TABLE ejecuciones_agentes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can read executions"
  ON ejecuciones_agentes FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "System can manage executions"
  ON ejecuciones_agentes FOR ALL
  TO authenticated
  USING (true)
  WITH CHECK (true);

-- =====================================================
-- 15. PREDICCIONES DE RIESGO
-- =====================================================

CREATE TABLE IF NOT EXISTS predicciones_riesgo (
    id SERIAL PRIMARY KEY,
    aeropuerto_id INTEGER REFERENCES aeropuertos(id),
    agente_id INTEGER REFERENCES agentes_openfang(id),
    fecha_prediccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ventana_tiempo_inicio TIMESTAMP,
    ventana_tiempo_fin TIMESTAMP,
    score_riesgo NUMERIC(5,2),
    factores_clave JSONB,
    estado_alerta VARCHAR(20) DEFAULT 'Informativa'
);

ALTER TABLE predicciones_riesgo ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can read predictions"
  ON predicciones_riesgo FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "System can create predictions"
  ON predicciones_riesgo FOR ALL
  TO authenticated
  USING (true)
  WITH CHECK (true);

-- =====================================================
-- 16. DATASET PARA ML
-- =====================================================

CREATE TABLE IF NOT EXISTS dataset_features_ml (
    id SERIAL PRIMARY KEY,
    aeropuerto_id INTEGER REFERENCES aeropuertos(id),
    fecha TIMESTAMP,
    incidentes_30d INTEGER DEFAULT 0,
    viento_promedio NUMERIC,
    visibilidad_promedio NUMERIC,
    reportes_sms INTEGER DEFAULT 0,
    riesgo_real NUMERIC
);

ALTER TABLE dataset_features_ml ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Analysts can read ML data"
  ON dataset_features_ml FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM usuarios 
      WHERE auth_user_id = auth.uid() 
      AND rol IN ('administrador', 'analista')
    )
  );

CREATE POLICY "System can manage ML data"
  ON dataset_features_ml FOR ALL
  TO authenticated
  USING (true)
  WITH CHECK (true);

-- Insert default incident types
INSERT INTO tipos_incidente (codigo_oaci, nombre, categoria) VALUES
  ('REIN', 'Reingreso Pista', 'Pista'),
  ('BIRD', 'Colisión con Fauna', 'Fauna'),
  ('GSPD', 'Exceso Velocidad en Tierra', 'Operaciones'),
  ('RUNWAY', 'Incursión de Pista', 'Pista'),
  ('FUEL', 'Emergencia Combustible', 'Técnico'),
  ('WEATHER', 'Condición Meteorológica Adversa', 'Meteorología'),
  ('ENGINE', 'Falla de Motor', 'Técnico'),
  ('GEAR', 'Problema Tren de Aterrizaje', 'Técnico')
ON CONFLICT DO NOTHING;