from __future__ import annotations

import csv
from pathlib import Path

import pyodbc


ROOT = Path(__file__).resolve().parents[1]
MDB_PATH = ROOT / "data" / "raw" / "avall.mdb"
OUT_DIR = ROOT / "data" / "processed" / "ntsb_full_export"
SUMMARY_PATH = ROOT / "data" / "processed" / "ntsb_full_export_summary.csv"
CHUNK_SIZE = 5000


def connect() -> pyodbc.Connection:
    conn_str = rf"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={MDB_PATH};"
    return pyodbc.connect(conn_str)


def list_tables(cursor: pyodbc.Cursor) -> list[str]:
    return [row.table_name for row in cursor.tables(tableType="TABLE")]


def export_table(cursor: pyodbc.Cursor, table_name: str) -> dict[str, int | str]:
    output_path = OUT_DIR / f"{table_name}.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    query = f"SELECT * FROM [{table_name}]"
    result = cursor.execute(query)
    columns = [column[0] for column in result.description]
    row_count = 0

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(columns)

        while True:
            rows = result.fetchmany(CHUNK_SIZE)
            if not rows:
                break
            for row in rows:
                writer.writerow(["" if value is None else value for value in row])
            row_count += len(rows)
            print(f"{table_name}: {row_count} rows exported", flush=True)

    return {
        "table_name": table_name,
        "row_count": row_count,
        "column_count": len(columns),
        "output_path": str(output_path.relative_to(ROOT)),
    }


def main() -> None:
    if not MDB_PATH.exists():
        raise FileNotFoundError(f"NTSB database not found: {MDB_PATH}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    with connect() as conn:
        cursor = conn.cursor()
        tables = list_tables(cursor)
        print(f"Found {len(tables)} tables", flush=True)

        summary_rows: list[dict[str, int | str]] = []
        for table_name in tables:
            print(f"Starting export for table: {table_name}", flush=True)
            summary_rows.append(export_table(cursor, table_name))

    with SUMMARY_PATH.open("w", newline="", encoding="utf-8") as summary_file:
        writer = csv.DictWriter(summary_file, fieldnames=["table_name", "row_count", "column_count", "output_path"])
        writer.writeheader()
        writer.writerows(summary_rows)

    print(f"Full export completed. Summary: {SUMMARY_PATH}", flush=True)


if __name__ == "__main__":
    main()
