from __future__ import annotations

from dotenv import load_dotenv

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.model_service import MODEL_PATH, bootstrap_bundle, load_ntsb_training_rows, save_bundle, train_bundle
from app.models import Incidente


def main() -> None:
    load_dotenv()
    ntsb_rows = load_ntsb_training_rows()
    bundle = train_bundle(ntsb_rows, source_name="ntsb-real") if len(ntsb_rows) >= 12 else None

    rows = []
    if bundle is None:
        with SessionLocal() as db:
            rows = [
                {
                    "aeropuerto_id": incidente.aeropuerto_id,
                    "tipo_incidente_id": incidente.tipo_incidente_id,
                    "aeronave_id": incidente.aeronave_id,
                    "fase_vuelo": incidente.fase_vuelo,
                    "descripcion": incidente.descripcion,
                    "latitud": incidente.latitud,
                    "longitud": incidente.longitud,
                    "fecha_hora": incidente.fecha_hora.isoformat(),
                    "nivel_riesgo": incidente.nivel_riesgo,
                }
                for incidente in db.scalars(select(Incidente).where(Incidente.nivel_riesgo.is_not(None)))
            ]

    if bundle is None and len(rows) >= 12:
        bundle = train_bundle(rows, source_name="postgresql")
    if bundle is None:
        bundle = bootstrap_bundle()

    path = save_bundle(bundle, MODEL_PATH)
    print(f"Modelo guardado en: {path}")
    print(f"Version: {bundle['model_version']}")
    print(f"Registros de entrenamiento: {bundle['training_rows']}")
    if bundle.get("metrics"):
        print(f"Accuracy holdout: {bundle['metrics']['accuracy']:.4f}")
        print(f"Train/Test: {bundle['metrics']['samples_train']}/{bundle['metrics']['samples_test']}")


if __name__ == "__main__":
    main()
