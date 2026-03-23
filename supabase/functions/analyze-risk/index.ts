import { createClient } from 'npm:@supabase/supabase-js@2';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Client-Info, Apikey',
};

Deno.serve(async (req: Request) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, {
      status: 200,
      headers: corsHeaders,
    });
  }

  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    const { aeropuerto_id } = await req.json();

    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

    const [incidentesRes, alertasRes, climaRes] = await Promise.all([
      supabase
        .from('incidentes')
        .select('nivel_riesgo, fecha_hora')
        .eq('aeropuerto_id', aeropuerto_id)
        .gte('fecha_hora', thirtyDaysAgo.toISOString()),
      supabase
        .from('alertas')
        .select('nivel_criticidad')
        .eq('aeropuerto_id', aeropuerto_id)
        .eq('estado', 'Pendiente'),
      supabase
        .from('condiciones_meteorologicas')
        .select('visibilidad_metros, viento_velocidad_kt, precipitacion')
        .eq('aeropuerto_id', aeropuerto_id)
        .gte('fecha_hora', thirtyDaysAgo.toISOString())
        .order('fecha_hora', { ascending: false })
        .limit(10)
    ]);

    const incidentes = incidentesRes.data || [];
    const alertas = alertasRes.data || [];
    const clima = climaRes.data || [];

    let riesgoScore = 0;
    const factores = [];

    if (incidentes.length > 5) {
      riesgoScore += 30;
      factores.push(`${incidentes.length} incidentes en últimos 30 días`);
    } else if (incidentes.length > 2) {
      riesgoScore += 15;
      factores.push(`${incidentes.length} incidentes en últimos 30 días`);
    }

    const incidentesCriticos = incidentes.filter(i => i.nivel_riesgo === 'Crítico' || i.nivel_riesgo === 'Alto');
    if (incidentesCriticos.length > 0) {
      riesgoScore += incidentesCriticos.length * 10;
      factores.push(`${incidentesCriticos.length} incidentes de alto riesgo`);
    }

    if (alertas.length > 3) {
      riesgoScore += 20;
      factores.push(`${alertas.length} alertas activas pendientes`);
    }

    const climaSevero = clima.filter(c =>
      (c.visibilidad_metros && c.visibilidad_metros < 1000) ||
      (c.viento_velocidad_kt && c.viento_velocidad_kt > 25) ||
      c.precipitacion
    );

    if (climaSevero.length > 5) {
      riesgoScore += 15;
      factores.push('Condiciones meteorológicas adversas frecuentes');
    }

    riesgoScore = Math.min(riesgoScore, 100);

    let nivelRiesgo = 'Bajo';
    if (riesgoScore >= 70) nivelRiesgo = 'Crítico';
    else if (riesgoScore >= 50) nivelRiesgo = 'Alto';
    else if (riesgoScore >= 30) nivelRiesgo = 'Medio';

    const analisis = {
      aeropuerto_id,
      score_riesgo: riesgoScore,
      nivel_riesgo: nivelRiesgo,
      factores_clave: factores,
      total_incidentes: incidentes.length,
      incidentes_criticos: incidentesCriticos.length,
      alertas_activas: alertas.length,
      clima_adverso: climaSevero.length,
      fecha_analisis: new Date().toISOString()
    };

    if (riesgoScore >= 50) {
      await supabase.from('alertas').insert({
        aeropuerto_id,
        tipo_alerta: 'Riesgo Elevado Detectado',
        nivel_criticidad: nivelRiesgo,
        mensaje: `Análisis automático detectó nivel de riesgo ${nivelRiesgo.toLowerCase()} (${riesgoScore}%). ${factores.join(', ')}.`,
        score_predictivo: riesgoScore,
        estado: 'Pendiente'
      });
    }

    return new Response(JSON.stringify(analisis), {
      headers: {
        ...corsHeaders,
        'Content-Type': 'application/json',
      },
    });
  } catch (error) {
    console.error('Error:', error);
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: {
        ...corsHeaders,
        'Content-Type': 'application/json',
      },
    });
  }
});
