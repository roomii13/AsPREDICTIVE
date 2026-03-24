from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "backend") not in sys.path:
    sys.path.insert(0, str(ROOT / "backend"))

from app.db import SessionLocal  # noqa: E402
from app.models import Aeronave, Aeropuerto, Incidente, TipoIncidente  # noqa: E402
from sqlalchemy import select  # noqa: E402


INPUT_PATH = ROOT / "data" / "processed" / "jst_incidentes_template.csv"
OUTPUT_PATH = ROOT / "data" / "processed" / "jst_training_base.csv"


def normalize_text(value: object) -> str:
    return "" if pd.isna(value) else str(value).strip()


def normalize_nullable_text(value: object) -> str | None:
    text = normalize_text(value)
    return text or None


def normalize_float(value: object) -> float | None:
    if pd.isna(value) or value in ("", None):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def normalize_datetime(value: object) -> str | None:
    text = normalize_text(value)
    if not text:
        return None
    parsed = pd.to_datetime(text, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.isoformat()


def load_jst_input(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, low_memory=False)
    required = [
        "source_record_id",
        "fecha_hora",
        "aeropuerto_icao",
        "aeropuerto_nombre",
        "tipo_incidente",
        "fase_vuelo",
        "descripcion",
        "nivel_riesgo",
    ]
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise ValueError(f"Faltan columnas requeridas en JST CSV: {', '.join(missing)}")
    return frame


def to_training_frame(frame: pd.DataFrame) -> pd.DataFrame:
    records: list[dict[str, object]] = []
    for _, row in frame.iterrows():
        records.append(
            {
                "fuente": "JST",
                "source_record_id": normalize_text(row.get("source_record_id")),
                "fecha_hora": normalize_datetime(row.get("fecha_hora")),
                "fecha": pd.to_datetime(row.get("fecha_hora"), errors="coerce").date().isoformat() if not pd.isna(pd.to_datetime(row.get("fecha_hora"), errors="coerce")) else None,
                "hora": pd.to_datetime(row.get("fecha_hora"), errors="coerce").strftime("%H%M") if not pd.isna(pd.to_datetime(row.get("fecha_hora"), errors="coerce")) else None,
                "aeropuerto_icao": normalize_nullable_text(row.get("aeropuerto_icao")),
                "aeropuerto_nombre": normalize_nullable_text(row.get("aeropuerto_nombre")),
                "ciudad": normalize_nullable_text(row.get("ciudad")),
                "provincia": normalize_nullable_text(row.get("provincia")),
                "fase_vuelo": normalize_nullable_text(row.get("fase_vuelo")),
                "descripcion": normalize_nullable_text(row.get("descripcion")),
                "tipo_incidente": normalize_nullable_text(row.get("tipo_incidente")),
                "categoria_incidente": normalize_nullable_text(row.get("categoria_incidente")),
                "aeronave_modelo": normalize_nullable_text(row.get("aeronave_modelo")),
                "aeronave_matricula": normalize_nullable_text(row.get("aeronave_matricula")),
                "tipo_aeronave": normalize_nullable_text(row.get("tipo_aeronave")),
                "condicion_meteorologica": normalize_nullable_text(row.get("condicion_meteorologica")),
                "condicion_luz": normalize_nullable_text(row.get("condicion_luz")),
                "visibilidad_millas": normalize_float(row.get("visibilidad_millas")),
                "viento_kt": normalize_float(row.get("viento_kt")),
                "latitud": normalize_float(row.get("latitud")),
                "longitud": normalize_float(row.get("longitud")),
                "lesionados": int(normalize_float(row.get("lesionados")) or 0),
                "fatalidades": int(normalize_float(row.get("fatalidades")) or 0),
                "nivel_riesgo": normalize_nullable_text(row.get("nivel_riesgo")),
            }
        )

    output = pd.DataFrame(records)
    output = output.dropna(subset=["fecha_hora", "descripcion", "nivel_riesgo"], how="any")
    return output


def export_training_csv(frame: pd.DataFrame, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output_path, index=False, encoding="utf-8")
    return output_path


def resolve_airport(db, row: pd.Series) -> Aeropuerto | None:
    aeropuerto_icao = normalize_nullable_text(row.get("aeropuerto_icao"))
    aeropuerto_nombre = normalize_nullable_text(row.get("aeropuerto_nombre"))

    if aeropuerto_icao:
        airport = db.scalar(select(Aeropuerto).where(Aeropuerto.codigo_icao == aeropuerto_icao))
        if airport:
            return airport

    if aeropuerto_nombre:
        return db.scalar(select(Aeropuerto).where(Aeropuerto.nombre == aeropuerto_nombre))

    return None


def resolve_incident_type(db, row: pd.Series) -> TipoIncidente | None:
    nombre = normalize_nullable_text(row.get("tipo_incidente"))
    categoria = normalize_nullable_text(row.get("categoria_incidente"))
    if not nombre:
        return None

    incident_type = db.scalar(select(TipoIncidente).where(TipoIncidente.nombre == nombre))
    if incident_type:
        if categoria and not incident_type.categoria:
            incident_type.categoria = categoria
        return incident_type

    incident_type = TipoIncidente(nombre=nombre, categoria=categoria, codigo_oaci=None)
    db.add(incident_type)
    db.flush()
    return incident_type


def resolve_aircraft(db, row: pd.Series) -> Aeronave | None:
    matricula = normalize_nullable_text(row.get("aeronave_matricula"))
    modelo = normalize_nullable_text(row.get("aeronave_modelo"))
    tipo = normalize_nullable_text(row.get("tipo_aeronave"))

    if matricula:
        aircraft = db.scalar(select(Aeronave).where(Aeronave.matricula == matricula))
        if aircraft:
            if modelo and not aircraft.modelo:
                aircraft.modelo = modelo
            if tipo and not aircraft.tipo_aeronave:
                aircraft.tipo_aeronave = tipo
            return aircraft

        aircraft = Aeronave(matricula=matricula, modelo=modelo, tipo_aeronave=tipo)
        db.add(aircraft)
        db.flush()
        return aircraft

    return None


def import_into_postgres(frame: pd.DataFrame) -> int:
    inserted = 0
    with SessionLocal() as db:
        for _, row in frame.iterrows():
            fecha_hora = pd.to_datetime(row["fecha_hora"], errors="coerce")
            if pd.isna(fecha_hora):
                continue

            airport = resolve_airport(db, row)
            incident_type = resolve_incident_type(db, row)
            aircraft = resolve_aircraft(db, row)
            descripcion = normalize_nullable_text(row.get("descripcion"))

            duplicate = db.scalar(
                select(Incidente).where(
                    Incidente.fecha_hora == fecha_hora.to_pydatetime(),
                    Incidente.descripcion == descripcion,
                    Incidente.aeropuerto_id == (airport.id if airport else None),
                )
            )
            if duplicate:
                continue

            incidente = Incidente(
                aeropuerto_id=airport.id if airport else None,
                tipo_incidente_id=incident_type.id if incident_type else None,
                aeronave_id=aircraft.id if aircraft else None,
                fecha_hora=fecha_hora.to_pydatetime(),
                descripcion=descripcion,
                nivel_riesgo=normalize_nullable_text(row.get("nivel_riesgo")),
                fase_vuelo=normalize_nullable_text(row.get("fase_vuelo")),
                condicion_meteorologica=normalize_nullable_text(row.get("condicion_meteorologica")),
                condicion_luz=normalize_nullable_text(row.get("condicion_luz")),
                visibilidad_millas=normalize_float(row.get("visibilidad_millas")),
                viento_kt=normalize_float(row.get("viento_kt")),
                latitud=normalize_float(row.get("latitud")),
                longitud=normalize_float(row.get("longitud")),
            )
            db.add(incidente)
            inserted += 1

        db.commit()

    return inserted


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Importa incidentes JST Argentina al dataset y opcionalmente a PostgreSQL.")
    parser.add_argument("--input", type=Path, default=INPUT_PATH, help="CSV fuente con incidentes JST normalizados.")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH, help="CSV de salida listo para entrenamiento.")
    parser.add_argument("--skip-db", action="store_true", help="Solo exporta CSV de entrenamiento y no inserta en PostgreSQL.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = load_jst_input(args.input)
    training_frame = to_training_frame(source)
    export_path = export_training_csv(training_frame, args.output)
    print(f"CSV JST exportado a: {export_path}")
    print(f"Registros JST listos para entrenamiento: {len(training_frame)}")

    if not args.skip_db:
        inserted = import_into_postgres(training_frame)
        print(f"Incidentes JST insertados en PostgreSQL: {inserted}")


if __name__ == "__main__":
    main()
