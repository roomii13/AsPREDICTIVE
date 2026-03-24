param(
  [string]$DatabaseUrl = $env:DATABASE_URL,
  [string]$OutputDir = "backups"
)

if (-not $DatabaseUrl) {
  Write-Error "DATABASE_URL no está definida."
  exit 1
}

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$outputFile = Join-Path $OutputDir "aspredictive_backup_$timestamp.sql"

pg_dump --dbname="$DatabaseUrl" --file="$outputFile" --format=p

if ($LASTEXITCODE -ne 0) {
  Write-Error "Falló el backup con pg_dump."
  exit $LASTEXITCODE
}

Write-Output "Backup generado en: $outputFile"
