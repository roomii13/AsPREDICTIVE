# Operación y hardening técnico

## Controles incorporados

- Logging estructurado de requests y errores del backend
- Endpoint de salud: `/health`
- Endpoint de métricas del modelo: `/model/metrics`
- Auditoría de acciones críticas en `audit_logs`
- Recuperación de acceso con token administrativo
- Entrenamiento automático del modelo en cada deploy de Render

## Backups

Script incluido:

- [backup_postgres.ps1](/C:/Users/Hugo%20Celis/OneDrive/Escritorio/AsPREDICTIVE/scripts/backup_postgres.ps1)

Uso:

```powershell
$env:DATABASE_URL="postgresql+psycopg://..."
.\scripts\backup_postgres.ps1
```

## Monitoreo recomendado

- Render: health checks y logs
- Neon: métricas y storage
- Uptime externo: UptimeRobot o Better Stack

## Política mínima sugerida

- Backup diario
- Retención de 14 a 30 días
- Revisión semanal de `audit_logs`
- Reentrenamiento del modelo quincenal o mensual
