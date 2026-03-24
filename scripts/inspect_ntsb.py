from __future__ import annotations

import pyodbc


def main() -> None:
    conn = pyodbc.connect(r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=data\raw\avall.mdb;")
    cur = conn.cursor()

    rows = cur.execute(
        "SELECT TOP 5 ev_id, ntsb_no, ev_date, ev_city, ev_state, ev_country FROM events ORDER BY ev_date DESC"
    ).fetchall()
    print("latest_rows:", rows)

    count_2015 = cur.execute("SELECT COUNT(*) FROM events WHERE ev_date >= #1/1/2015#").fetchone()[0]
    print("events_since_2015:", count_2015)


if __name__ == "__main__":
    main()
