from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

from .schemas import IncidentePayload, NivelRiesgo


ROOT_DIR = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT_DIR / "models"
MODEL_PATH = MODEL_DIR / "risk_model.joblib"
PROJECT_ROOT = ROOT_DIR.parent
NTSB_TRAINING_PATH = PROJECT_ROOT / "data" / "processed" / "ntsb_training_base.csv"
RISK_ORDER: list[NivelRiesgo] = ["Bajo", "Medio", "Alto", "Crítico"]
RISK_WEIGHTS = np.array([25.0, 50.0, 75.0, 100.0])


def _normalize_text(value: str | None) -> str:
    return (value or "").strip().lower()


def build_feature_frame(rows: list[dict[str, Any]]) -> pd.DataFrame:
    frame = pd.DataFrame(rows)
    if frame.empty:
        frame = pd.DataFrame([{}])

    def column(name: str, default: Any) -> pd.Series:
        if name in frame.columns:
            return frame[name]
        return pd.Series([default] * len(frame), index=frame.index)

    frame["descripcion"] = column("descripcion", "").fillna("").astype(str)
    frame["fase_vuelo"] = column("fase_vuelo", "").fillna("").astype(str)
    frame["condicion_meteorologica"] = column("condicion_meteorologica", "").fillna("").astype(str)
    frame["condicion_luz"] = column("condicion_luz", "").fillna("").astype(str)
    frame["cielo_sin_techo"] = column("cielo_sin_techo", "").fillna("").astype(str)
    frame["cielo_con_techo"] = column("cielo_con_techo", "").fillna("").astype(str)
    frame["aeropuerto_id"] = pd.to_numeric(column("aeropuerto_id", -1), errors="coerce").fillna(-1).astype(int).astype(str)
    frame["tipo_incidente_id"] = pd.to_numeric(column("tipo_incidente_id", -1), errors="coerce").fillna(-1).astype(int).astype(str)
    frame["aeronave_id"] = pd.to_numeric(column("aeronave_id", -1), errors="coerce").fillna(-1).astype(int).astype(str)
    raw_latitud = pd.to_numeric(column("latitud", np.nan), errors="coerce")
    raw_longitud = pd.to_numeric(column("longitud", np.nan), errors="coerce")
    frame["has_coordinates"] = (~raw_latitud.isna() & ~raw_longitud.isna()).astype(int)
    frame["latitud"] = raw_latitud.fillna(0.0)
    frame["longitud"] = raw_longitud.fillna(0.0)
    frame["visibilidad_millas"] = pd.to_numeric(column("visibilidad_millas", np.nan), errors="coerce").fillna(0.0)
    frame["viento_kt"] = pd.to_numeric(column("viento_kt", np.nan), errors="coerce").fillna(0.0)
    frame["viento_dir_deg"] = pd.to_numeric(column("viento_dir_deg", np.nan), errors="coerce").fillna(0.0)
    frame["temperatura_c"] = pd.to_numeric(column("temperatura_c", np.nan), errors="coerce").fillna(0.0)
    frame["punto_rocio_c"] = pd.to_numeric(column("punto_rocio_c", np.nan), errors="coerce").fillna(0.0)
    frame["techo_nubes_ft"] = pd.to_numeric(column("techo_nubes_ft", np.nan), errors="coerce").fillna(0.0)
    frame["precipitacion"] = column("intensidad_precipitacion", "").fillna("").astype(str).map(lambda value: 0 if value.strip() == "" else 1)

    fecha = pd.to_datetime(column("fecha_hora", None), errors="coerce", utc=True)
    frame["hour"] = fecha.dt.hour.fillna(12).astype(int)
    frame["day_of_week"] = fecha.dt.dayofweek.fillna(0).astype(int)
    frame["month"] = fecha.dt.month.fillna(1).astype(int)
    frame["is_night"] = frame["hour"].apply(lambda value: 1 if value >= 20 or value <= 5 else 0)

    frame["descripcion"] = frame["descripcion"].map(_normalize_text)
    frame["fase_vuelo"] = frame["fase_vuelo"].map(_normalize_text)
    frame["condicion_meteorologica"] = frame["condicion_meteorologica"].map(_normalize_text)
    frame["condicion_luz"] = frame["condicion_luz"].map(_normalize_text)
    frame["cielo_sin_techo"] = frame["cielo_sin_techo"].map(_normalize_text)
    frame["cielo_con_techo"] = frame["cielo_con_techo"].map(_normalize_text)

    return frame[
        [
            "descripcion",
            "fase_vuelo",
            "condicion_meteorologica",
            "condicion_luz",
            "cielo_sin_techo",
            "cielo_con_techo",
            "aeropuerto_id",
            "tipo_incidente_id",
            "aeronave_id",
            "latitud",
            "longitud",
            "visibilidad_millas",
            "viento_kt",
            "viento_dir_deg",
            "temperatura_c",
            "punto_rocio_c",
            "techo_nubes_ft",
            "precipitacion",
            "hour",
            "day_of_week",
            "month",
            "is_night",
            "has_coordinates",
        ]
    ]


def create_training_rows() -> list[dict[str, Any]]:
    base_rows = [
        {
            "descripcion": "colision con fauna durante aterrizaje con visibilidad reducida",
            "fase_vuelo": "Aterrizaje",
            "aeropuerto_id": 1,
            "tipo_incidente_id": 2,
            "aeronave_id": 11,
            "latitud": -34.81,
            "longitud": -58.53,
            "fecha_hora": "2026-03-18T22:10:00Z",
            "nivel_riesgo": "Crítico",
        },
        {
            "descripcion": "falla de motor en ascenso inicial con vibraciones",
            "fase_vuelo": "Despegue",
            "aeropuerto_id": 2,
            "tipo_incidente_id": 7,
            "aeronave_id": 8,
            "latitud": -31.29,
            "longitud": -64.21,
            "fecha_hora": "2026-03-02T04:25:00Z",
            "nivel_riesgo": "Crítico",
        },
        {
            "descripcion": "incursion de pista con aproximacion frustrada",
            "fase_vuelo": "Aterrizaje",
            "aeropuerto_id": 3,
            "tipo_incidente_id": 4,
            "aeronave_id": 19,
            "latitud": -32.91,
            "longitud": -60.79,
            "fecha_hora": "2026-02-21T23:55:00Z",
            "nivel_riesgo": "Alto",
        },
        {
            "descripcion": "condicion meteorologica adversa con viento cruzado fuerte",
            "fase_vuelo": "Aterrizaje",
            "aeropuerto_id": 5,
            "tipo_incidente_id": 6,
            "aeronave_id": 5,
            "latitud": -34.56,
            "longitud": -58.42,
            "fecha_hora": "2026-01-17T21:00:00Z",
            "nivel_riesgo": "Alto",
        },
        {
            "descripcion": "exceso de velocidad en rodaje sin daños reportados",
            "fase_vuelo": "Rodaje",
            "aeropuerto_id": 1,
            "tipo_incidente_id": 3,
            "aeronave_id": 9,
            "latitud": -34.82,
            "longitud": -58.54,
            "fecha_hora": "2026-03-11T14:00:00Z",
            "nivel_riesgo": "Medio",
        },
        {
            "descripcion": "reporte preventivo por objeto extraño cercano a pista",
            "fase_vuelo": "Rodaje",
            "aeropuerto_id": 4,
            "tipo_incidente_id": 1,
            "aeronave_id": 14,
            "latitud": -24.85,
            "longitud": -65.49,
            "fecha_hora": "2026-03-01T11:40:00Z",
            "nivel_riesgo": "Medio",
        },
        {
            "descripcion": "demora operacional menor durante crucero sin impacto",
            "fase_vuelo": "Crucero",
            "aeropuerto_id": 6,
            "tipo_incidente_id": 3,
            "aeronave_id": 12,
            "latitud": -38.0,
            "longitud": -57.56,
            "fecha_hora": "2026-02-12T16:30:00Z",
            "nivel_riesgo": "Bajo",
        },
        {
            "descripcion": "chequeo de mantenimiento por indicacion preventiva",
            "fase_vuelo": "En tierra",
            "aeropuerto_id": 7,
            "tipo_incidente_id": 8,
            "aeronave_id": 2,
            "latitud": None,
            "longitud": None,
            "fecha_hora": "2026-01-08T09:20:00Z",
            "nivel_riesgo": "Bajo",
        },
    ]

    rows: list[dict[str, Any]] = []
    variants = [
        ("Crítico", 22, "emergencia", "Despegue"),
        ("Alto", 14, "desviacion", "Aterrizaje"),
        ("Medio", 10, "precaucion", "Rodaje"),
        ("Bajo", 8, "preventivo", "Crucero"),
    ]

    for template in base_rows:
        rows.append(template)

    for risk, count, suffix, phase in variants:
        for index in range(count):
            base = base_rows[index % len(base_rows)].copy()
            base["nivel_riesgo"] = risk
            base["fase_vuelo"] = phase
            base["descripcion"] = f"{base['descripcion']} {suffix} caso {index + 1}"
            base["aeropuerto_id"] = (index % 7) + 1
            base["tipo_incidente_id"] = (index % 8) + 1
            base["aeronave_id"] = (index % 20) + 1
            base["fecha_hora"] = f"2026-02-{(index % 27) + 1:02d}T{(index % 24):02d}:00:00Z"
            rows.append(base)

    return rows


def create_model_pipeline() -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            ("descripcion", TfidfVectorizer(max_features=150, ngram_range=(1, 2)), "descripcion"),
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                [
                    "fase_vuelo",
                    "condicion_meteorologica",
                    "condicion_luz",
                    "cielo_sin_techo",
                    "cielo_con_techo",
                    "aeropuerto_id",
                    "tipo_incidente_id",
                    "aeronave_id",
                ],
            ),
            (
                "numeric",
                StandardScaler(with_mean=False),
                [
                    "latitud",
                    "longitud",
                    "visibilidad_millas",
                    "viento_kt",
                    "viento_dir_deg",
                    "temperatura_c",
                    "punto_rocio_c",
                    "techo_nubes_ft",
                    "precipitacion",
                    "hour",
                    "day_of_week",
                    "month",
                    "is_night",
                    "has_coordinates",
                ],
            ),
        ]
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1500,
                    class_weight="balanced",
                    random_state=42,
                ),
            ),
        ]
    )


def load_ntsb_training_rows(path: Path = NTSB_TRAINING_PATH) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    frame = pd.read_csv(path, low_memory=False)
    if frame.empty:
        return []

    rows: list[dict[str, Any]] = []
    for _, row in frame.iterrows():
        rows.append(
            {
                "aeropuerto_id": None,
                "tipo_incidente_id": None,
                "aeronave_id": None,
                "fase_vuelo": row.get("fase_vuelo"),
                "condicion_meteorologica": row.get("condicion_meteorologica"),
                "condicion_luz": row.get("condicion_luz"),
                "cielo_sin_techo": row.get("cielo_sin_techo"),
                "cielo_con_techo": row.get("cielo_con_techo"),
                "descripcion": row.get("descripcion"),
                "latitud": row.get("latitud"),
                "longitud": row.get("longitud"),
                "visibilidad_millas": row.get("visibilidad_millas"),
                "viento_kt": row.get("viento_kt"),
                "viento_dir_deg": row.get("viento_dir_deg"),
                "temperatura_c": row.get("temperatura_c"),
                "punto_rocio_c": row.get("punto_rocio_c"),
                "techo_nubes_ft": row.get("techo_nubes_ft"),
                "intensidad_precipitacion": row.get("intensidad_precipitacion"),
                "fecha_hora": _combine_fecha_hora(row.get("fecha"), row.get("hora")),
                "nivel_riesgo": row.get("nivel_riesgo"),
            }
        )

    return rows


def _combine_fecha_hora(fecha: Any, hora: Any) -> str | None:
    if pd.isna(fecha):
        return None
    fecha_ts = pd.to_datetime(fecha, errors="coerce")
    if pd.isna(fecha_ts):
        return None

    if pd.isna(hora):
        return fecha_ts.isoformat()

    try:
        hour_value = int(float(hora))
        hours = hour_value // 100
        minutes = hour_value % 100
        fecha_ts = fecha_ts.replace(hour=hours, minute=minutes)
    except Exception:
        pass

    return fecha_ts.isoformat()


def train_bundle(rows: list[dict[str, Any]], source_name: str) -> dict[str, Any]:
    training_rows = [row for row in rows if row.get("nivel_riesgo") in RISK_ORDER]
    if len(training_rows) < 12:
        raise ValueError("Se requieren al menos 12 registros etiquetados para entrenar el modelo.")

    frame = build_feature_frame(training_rows)
    target = [row["nivel_riesgo"] for row in training_rows]

    pipeline = create_model_pipeline()
    x_train, x_test, y_train, y_test = train_test_split(
        frame,
        target,
        test_size=0.2,
        random_state=42,
        stratify=target,
    )
    pipeline.fit(x_train, y_train)
    predictions = pipeline.predict(x_test)
    accuracy = float(accuracy_score(y_test, predictions))
    report = classification_report(y_test, predictions, output_dict=True, zero_division=0)

    return {
        "pipeline": pipeline,
        "risk_order": RISK_ORDER,
        "risk_weights": RISK_WEIGHTS.tolist(),
        "model_version": f"logreg-multiclass-{source_name}",
        "training_rows": len(training_rows),
        "metrics": {
            "accuracy": accuracy,
            "samples_train": len(x_train),
            "samples_test": len(x_test),
            "classification_report": report,
        },
    }


def save_bundle(bundle: dict[str, Any], path: Path = MODEL_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, path)
    return path


def bootstrap_bundle() -> dict[str, Any]:
    return train_bundle(create_training_rows(), source_name="bootstrap")


def best_available_training_bundle() -> dict[str, Any]:
    ntsb_rows = load_ntsb_training_rows()
    if len(ntsb_rows) >= 12:
        return train_bundle(ntsb_rows, source_name="ntsb-real")
    return bootstrap_bundle()


@dataclass
class PredictionResult:
    score: int
    nivel: NivelRiesgo
    factores: list[str]
    modelo: str


class RiskPredictor:
    def __init__(self, model_path: Path = MODEL_PATH):
        self.model_path = model_path
        self.bundle = self._load_or_bootstrap()

    def _load_or_bootstrap(self) -> dict[str, Any]:
        if self.model_path.exists():
            return joblib.load(self.model_path)

        bundle = best_available_training_bundle()
        save_bundle(bundle, self.model_path)
        return bundle

    @property
    def model_version(self) -> str:
        return str(self.bundle["model_version"])

    def reload(self) -> None:
        self.bundle = self._load_or_bootstrap()

    def predict(self, payload: IncidentePayload) -> PredictionResult:
        row = build_feature_frame([payload.model_dump()])
        pipeline: Pipeline = self.bundle["pipeline"]
        classifier: LogisticRegression = pipeline.named_steps["classifier"]
        probabilities = pipeline.predict_proba(row)[0]
        class_weights = np.array(
            [self._risk_weight_for_label(str(label)) for label in classifier.classes_],
            dtype=float,
        )
        weighted_score = float(np.dot(probabilities, class_weights))
        predicted_label = self._score_to_level(weighted_score)
        factors = self._explain_prediction(row, probabilities)

        return PredictionResult(
            score=int(round(weighted_score)),
            nivel=predicted_label,
            factores=factors,
            modelo=self.model_version,
        )

    def _risk_weight_for_label(self, label: str) -> float:
        mapping = {
            "Bajo": 25.0,
            "Medio": 50.0,
            "Alto": 75.0,
            "Crítico": 100.0,
        }
        return mapping.get(label, 50.0)

    def _score_to_level(self, score: float) -> NivelRiesgo:
        if score >= 85:
            return "Crítico"
        if score >= 70:
            return "Alto"
        if score >= 50:
            return "Medio"
        return "Bajo"

    def _explain_prediction(self, row: pd.DataFrame, probabilities: np.ndarray) -> list[str]:
        pipeline: Pipeline = self.bundle["pipeline"]
        preprocessor: ColumnTransformer = pipeline.named_steps["preprocessor"]
        classifier: LogisticRegression = pipeline.named_steps["classifier"]
        transformed = preprocessor.transform(row)
        if not sparse.issparse(transformed):
            transformed = sparse.csr_matrix(transformed)

        class_index = int(np.argmax(probabilities))
        feature_names = preprocessor.get_feature_names_out()
        class_coef = classifier.coef_[class_index]
        row_values = transformed.toarray()[0]
        contributions = row_values * class_coef
        top_indexes = np.argsort(contributions)[-4:][::-1]

        explanations: list[str] = []
        for idx in top_indexes:
            contribution = contributions[idx]
            if contribution <= 0:
                continue
            name = feature_names[idx].replace("__", ": ").replace("_", " ")
            explanations.append(f"{name} (+{contribution:.2f})")

        if not explanations:
            explanations.append("sin factores dominantes identificados")

        return explanations
