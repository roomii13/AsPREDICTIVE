# Datos oficiales para entrenamiento

Esta carpeta organiza fuentes oficiales de aviación y clima para construir datasets reales.

## Estructura

- `raw/`: archivos descargados directamente desde fuentes oficiales
- `processed/`: CSVs listos para inspección o para una etapa posterior de entrenamiento

## Qué dejé preparado

- `processed/source_catalog.csv`: catálogo de fuentes oficiales recomendadas
- `processed/official_raw_files.csv`: inventario de archivos descargados o pendientes
- `processed/training_incidentes_template.csv`: esquema base del dataset de incidentes
- `scripts/fetch_official_aviation_data.py`: descarga fuentes oficiales

## Fuente descargada

- `raw/ntsb_avall.zip`
  Descarga oficial de NTSB iniciada desde el dataset histórico de aviación.
  Si el archivo está incompleto o corrupto, vuelve a descargarlo con el script.

## Próximo paso recomendado

1. Ejecutar `scripts/fetch_official_aviation_data.py`
2. Verificar las descargas en `data/raw`
3. Parsear el dataset NTSB o exportarlo a CSV con una etapa adicional
4. Cruzar incidentes con METAR por aeropuerto y fecha/hora
