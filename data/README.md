# Datos oficiales para entrenamiento

Esta carpeta organiza fuentes oficiales de aviacion y clima para construir datasets reales.

## Estructura

- `raw/`: archivos descargados directamente desde fuentes oficiales
- `processed/`: CSV listos para inspeccion o entrenamiento

## Que quedo preparado

- `processed/source_catalog.csv`: catalogo de fuentes oficiales recomendadas
- `processed/official_raw_files.csv`: inventario de archivos descargados o pendientes
- `processed/training_incidentes_template.csv`: esquema general del dataset de incidentes
- `processed/jst_incidentes_template.csv`: plantilla de carga para incidentes argentinos JST
- `scripts/fetch_official_aviation_data.py`: descarga fuentes oficiales
- `scripts/import_jst_argentina.py`: transforma JST a CSV de entrenamiento e inserta incidentes en PostgreSQL

## Fuentes ya trabajadas

- `raw/ntsb_avall.zip`
- `processed/ntsb_training_base.csv`
- `processed/metars_current.csv`
- `processed/stations_current.csv`

## Importar JST Argentina

1. Completa `processed/jst_incidentes_template.csv` con incidentes argentinos reales.
2. Ejecuta:

```bash
python scripts/import_jst_argentina.py
```

Eso hace dos cosas:

- genera `processed/jst_training_base.csv`
- inserta incidentes en PostgreSQL si la base esta configurada

Si solo quieres generar el CSV de entrenamiento sin tocar la base:

```bash
python scripts/import_jst_argentina.py --skip-db
```

## Entrenamiento posterior

El backend ya quedo preparado para entrenar con estas capas:

1. NTSB historico
2. JST Argentina importado
3. incidentes reales de tu propia operacion en PostgreSQL
4. bootstrap sintetico solo como ultimo fallback
