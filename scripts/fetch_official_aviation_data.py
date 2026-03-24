from __future__ import annotations

import csv
import gzip
import json
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"


SOURCES = [
    {
        "name": "ntsb_avall.zip",
        "url": r"https://data.ntsb.gov/avdata/FileDirectory/DownloadFile?fileID=C:\avdata\avall.zip",
        "kind": "binary",
    },
    {
        "name": "metars.cache.csv.gz",
        "url": "https://aviationweather.gov/data/cache/metars.cache.csv.gz",
        "kind": "gzip_csv",
    },
    {
        "name": "stations.cache.json.gz",
        "url": "https://aviationweather.gov/data/cache/stations.cache.json.gz",
        "kind": "gzip_json",
    },
]


def download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 AsPREDICTIVE data fetcher"})
    with urlopen(request, timeout=120) as response:  # nosec B310
        destination.write_bytes(response.read())


def maybe_extract_metars(gzip_path: Path, output_csv: Path) -> None:
    with gzip.open(gzip_path, "rt", encoding="utf-8", errors="replace") as source:
        content = source.read()
    output_csv.write_text(content, encoding="utf-8")


def maybe_extract_stations(gzip_path: Path, output_csv: Path) -> None:
    with gzip.open(gzip_path, "rt", encoding="utf-8", errors="replace") as source:
        payload = json.load(source)

    rows = payload if isinstance(payload, list) else payload.get("data", [])
    if not rows:
        return

    fieldnames = sorted({key for row in rows for key in row.keys()})
    with output_csv.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)

    for source in SOURCES:
        destination = RAW / source["name"]
        print(f"Downloading {source['url']} -> {destination}")
        try:
            download(source["url"], destination)
        except Exception as error:
            print(f"Skipping {source['name']}: {error}")
            continue

        if source["kind"] == "gzip_csv":
            maybe_extract_metars(destination, PROCESSED / "metars_current.csv")
            print("Extracted metars_current.csv")
        elif source["kind"] == "gzip_json":
            maybe_extract_stations(destination, PROCESSED / "stations_current.csv")
            print("Extracted stations_current.csv")

    print("Official aviation data download complete.")


if __name__ == "__main__":
    main()
