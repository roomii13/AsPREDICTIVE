from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EXPORT_DIR = ROOT / "data" / "processed" / "ntsb_full_export"
OUT_PATH = ROOT / "data" / "processed" / "ntsb_training_base.csv"


def read_csv(name: str, usecols: list[str] | None = None) -> pd.DataFrame:
    return pd.read_csv(EXPORT_DIR / name, usecols=usecols, low_memory=False)


def normalize_text(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.replace(r"\s+", " ", regex=True).str.strip()


def derive_risk_level(row: pd.Series) -> str:
    fatal = int(row.get("fatal_count", 0) or 0)
    serious = int(row.get("serious_count", 0) or 0)
    minor = int(row.get("minor_count", 0) or 0)
    total = int(row.get("total_injured_count", 0) or 0)
    damage = str(row.get("damage", "") or "").strip().upper()

    if fatal > 0 or damage == "DEST":
        return "Crítico"
    if serious > 0 or damage == "SUBS":
        return "Alto"
    if minor > 0 or damage == "MINR":
        return "Medio"
    if total > 0:
        return "Medio"
    return "Bajo"


def main() -> None:
    events = read_csv(
        "events.csv",
        usecols=[
            "ev_id",
            "ntsb_no",
            "ev_type",
            "ev_date",
            "ev_time",
            "ev_city",
            "ev_state",
            "ev_country",
            "latitude",
            "longitude",
            "apt_name",
            "ev_nr_apt_id",
            "light_cond",
            "sky_cond_nonceil",
            "sky_ceil_ht",
            "sky_cond_ceil",
            "vis_sm",
            "wx_obs_time",
            "wx_obs_fac_id",
            "wind_vel_kts",
            "wind_dir_deg",
            "wx_temp",
            "wx_dew_pt",
            "wx_int_precip",
            "wx_cond_basic",
        ],
    )

    aircraft = read_csv(
        "aircraft.csv",
        usecols=[
            "ev_id",
            "Aircraft_Key",
            "damage",
            "acft_make",
            "acft_model",
            "acft_series",
            "regis_no",
            "far_part",
            "total_seats",
            "acft_category",
        ],
    )

    injury = read_csv(
        "injury.csv",
        usecols=["ev_id", "Aircraft_Key", "injury_level", "inj_person_count"],
    )

    narratives = read_csv(
        "narratives.csv",
        usecols=["ev_id", "Aircraft_Key", "narr_cause", "narr_accf", "narr_inc"],
    )

    events_sequence = read_csv(
        "Events_Sequence.csv",
        usecols=["ev_id", "Occurrence_Description", "Defining_ev", "Occurrence_No"],
    )

    aircraft_primary = aircraft.sort_values(["ev_id", "Aircraft_Key"]).drop_duplicates(subset=["ev_id"], keep="first")
    narrative_primary = narratives.sort_values(["ev_id", "Aircraft_Key"]).drop_duplicates(subset=["ev_id"], keep="first")
    phase_primary = (
        events_sequence.sort_values(["ev_id", "Defining_ev", "Occurrence_No"], ascending=[True, False, True])
        .drop_duplicates(subset=["ev_id"], keep="first")
        .rename(columns={"Occurrence_Description": "fase_vuelo"})
    )

    injury_summary = (
        injury.pivot_table(
            index="ev_id",
            columns="injury_level",
            values="inj_person_count",
            aggfunc="sum",
            fill_value=0,
        )
        .reset_index()
        .rename_axis(None, axis=1)
    )

    injury_summary = injury_summary.rename(
        columns={
            "FATL": "fatal_count",
            "SERS": "serious_count",
            "MINR": "minor_count",
            "NONE": "none_count",
            "TOTL": "total_injured_count",
        }
    )

    merged = (
        events.merge(aircraft_primary, on="ev_id", how="left")
        .merge(injury_summary, on="ev_id", how="left")
        .merge(phase_primary[["ev_id", "fase_vuelo"]], on="ev_id", how="left")
        .merge(narrative_primary[["ev_id", "narr_cause", "narr_accf", "narr_inc"]], on="ev_id", how="left")
    )

    for column in ["fatal_count", "serious_count", "minor_count", "none_count", "total_injured_count"]:
        if column not in merged.columns:
            merged[column] = 0
        merged[column] = merged[column].fillna(0).astype(int)

    merged["descripcion"] = normalize_text(merged["narr_cause"]) + " " + normalize_text(merged["narr_accf"]) + " " + normalize_text(merged["narr_inc"])
    merged["descripcion"] = normalize_text(merged["descripcion"])
    merged["fase_vuelo"] = normalize_text(merged["fase_vuelo"])
    merged["damage"] = merged["damage"].fillna("").astype(str)
    merged["nivel_riesgo"] = merged.apply(derive_risk_level, axis=1)
    merged["source"] = "NTSB"

    training = merged[
        [
            "source",
            "ev_id",
            "ntsb_no",
            "ev_type",
            "ev_date",
            "ev_time",
            "ev_city",
            "ev_state",
            "ev_country",
            "apt_name",
            "ev_nr_apt_id",
            "latitude",
            "longitude",
            "fase_vuelo",
            "light_cond",
            "sky_cond_nonceil",
            "sky_ceil_ht",
            "sky_cond_ceil",
            "vis_sm",
            "wx_obs_time",
            "wx_obs_fac_id",
            "wind_vel_kts",
            "wind_dir_deg",
            "wx_temp",
            "wx_dew_pt",
            "wx_int_precip",
            "wx_cond_basic",
            "damage",
            "acft_make",
            "acft_model",
            "acft_series",
            "regis_no",
            "far_part",
            "total_seats",
            "acft_category",
            "fatal_count",
            "serious_count",
            "minor_count",
            "none_count",
            "total_injured_count",
            "descripcion",
            "nivel_riesgo",
        ]
    ].rename(
        columns={
            "ev_id": "source_record_id",
            "ntsb_no": "investigation_id",
            "ev_type": "event_type",
            "ev_date": "fecha",
            "ev_time": "hora",
            "ev_city": "ciudad",
            "ev_state": "estado_region",
            "ev_country": "pais",
            "apt_name": "aeropuerto_nombre",
            "ev_nr_apt_id": "aeropuerto_icao",
            "latitude": "latitud",
            "longitude": "longitud",
            "light_cond": "condicion_luz",
            "sky_cond_nonceil": "cielo_sin_techo",
            "sky_ceil_ht": "techo_nubes_ft",
            "sky_cond_ceil": "cielo_con_techo",
            "vis_sm": "visibilidad_millas",
            "wx_obs_time": "metar_hora_obs",
            "wx_obs_fac_id": "metar_estacion",
            "wind_vel_kts": "viento_kt",
            "wind_dir_deg": "viento_dir_deg",
            "wx_temp": "temperatura_c",
            "wx_dew_pt": "punto_rocio_c",
            "wx_int_precip": "intensidad_precipitacion",
            "wx_cond_basic": "condicion_meteorologica",
            "damage": "damage_level",
            "acft_make": "fabricante",
            "acft_model": "aeronave_modelo",
            "acft_series": "aeronave_serie",
            "regis_no": "aeronave_matricula",
        }
    )

    training.to_csv(OUT_PATH, index=False)
    print(f"Created training base at {OUT_PATH}")
    print(f"Rows: {len(training)}")
    print(training["nivel_riesgo"].value_counts(dropna=False).to_string())


if __name__ == "__main__":
    main()
